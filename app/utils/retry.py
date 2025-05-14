from functools import wraps
import asyncio
import time
from datetime import timedelta
from typing import Callable, Optional, Union
import httpx
import random
from fastapi import HTTPException
from app.core.config import settings
import logging
from enum import Enum, auto

logger = logging.getLogger(__name__)

class BackoffStrategy(Enum):
    EXPONENTIAL = auto()
    LINEAR = auto()
    CONSTANT = auto()
    FIBONACCI = auto()

class CircuitBreaker:
    def __init__(self, max_failures=5, reset_timeout=60):
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.is_open = False
        self.metrics = {
            'total_failures': 0,
            'total_blocks': 0,
            'last_reset': None
        }

    def check_state(self):
        if self.is_open:
            if (time.time() - self.last_failure_time) > self.reset_timeout:
                self.is_open = False
                self.failure_count = 0
                self.metrics['last_reset'] = time.time()
                logger.info("Circuit breaker resetado")
                return True
            self.metrics['total_blocks'] += 1
            return False
        return True

    def record_failure(self):
        self.failure_count += 1
        self.metrics['total_failures'] += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.max_failures:
            self.is_open = True
            logger.error(f"Circuit breaker aberto após {self.failure_count} falhas")

def retry_request(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    retry_on: tuple = (500, 502, 503, 504),
    circuit_breaker: Optional[CircuitBreaker] = None,
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL,
    log_level: int = logging.WARNING
):
    """
    Decorator avançado para retentativas com múltiplas estratégias
    
    Args:
        max_retries: Número máximo de tentativas
        initial_delay: Atraso inicial em segundos
        max_delay: Atraso máximo em segundos
        backoff_factor: Fator de multiplicação para backoff
        retry_on: Códigos HTTP que disparam retentativas
        circuit_breaker: Instância de CircuitBreaker
        strategy: Estratégia de backoff (EXPONENTIAL, LINEAR, CONSTANT, FIBONACCI)
        log_level: Nível de log para tentativas
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_error = None
            if circuit_breaker and not circuit_breaker.check_state():
                logger.error("Circuit breaker aberto - requisição bloqueada")
                raise HTTPException(
                    status_code=503,
                    detail="Serviço temporariamente indisponível (circuit breaker)"
                )

            for attempt in range(max_retries + 1):
                try:
                    result = await func(*args, **kwargs)
                    if circuit_breaker:
                        circuit_breaker.failure_count = 0
                    return result
                except httpx.HTTPStatusError as e:
                    if e.response.status_code not in retry_on:
                        raise
                    last_error = e
                    if circuit_breaker:
                        circuit_breaker.record_failure()
                except Exception as e:
                    last_error = e
                    if circuit_breaker:
                        circuit_breaker.record_failure()

                if attempt < max_retries:
                    delay = _calculate_delay(
                        attempt, initial_delay, max_delay, backoff_factor, strategy
                    )
                    logger.log(
                        log_level,
                        f"Tentativa {attempt + 1}/{max_retries} falhou. "
                        f"Tentando novamente em {delay:.2f}s. Erro: {str(last_error)}"
                    )
                    await asyncio.sleep(delay)

            logger.error(f"Todas as {max_retries} tentativas falharam")
            raise HTTPException(
                status_code=503,
                detail=f"Serviço indisponível após {max_retries} tentativas"
            ) from last_error
        return wrapper
    return decorator

def _calculate_delay(
    attempt: int,
    initial_delay: float,
    max_delay: float,
    backoff_factor: float,
    strategy: BackoffStrategy
) -> float:
    """Calcula o tempo de espera baseado na estratégia"""
    jitter = random.uniform(0, 0.1 * initial_delay)
    
    if strategy == BackoffStrategy.EXPONENTIAL:
        delay = initial_delay * (backoff_factor ** attempt)
    elif strategy == BackoffStrategy.LINEAR:
        delay = initial_delay * (1 + attempt)
    elif strategy == BackoffStrategy.CONSTANT:
        delay = initial_delay
    elif strategy == BackoffStrategy.FIBONACCI:
        delay = initial_delay * _fibonacci(attempt + 1)
    else:
        delay = initial_delay
    
    return min(delay + jitter, max_delay)

def _fibonacci(n: int) -> int:
    """Calcula número de Fibonacci"""
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a