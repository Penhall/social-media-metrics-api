from functools import wraps
import time
from typing import Callable, Any, Optional
from enum import Enum, auto
from app.core.config import settings
from app.utils.api_cache import cache
import logging
from collections import deque

logger = logging.getLogger(__name__)

class Platform(Enum):
    FACEBOOK = auto()
    TWITTER = auto()
    INSTAGRAM = auto()
    TIKTOK = auto()

class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

# Limites por plataforma (chamadas/segundo)
PLATFORM_LIMITS = {
    Platform.FACEBOOK: 5,
    Platform.TWITTER: 3,
    Platform.INSTAGRAM: 2,
    Platform.TIKTOK: 4
}

request_queue = deque()

def rate_limited(platform: Platform, priority: Priority = Priority.MEDIUM):
    """
    Decorator avançado para limitar chamadas à API por plataforma
    
    Args:
        platform: Plataforma da API (enum Platform)
        priority: Prioridade da requisição (enum Priority)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            platform_limit = PLATFORM_LIMITS[platform]
            key = f"rate_limit:{platform.name}:{func.__name__}"

            # Adiciona à fila de espera se necessário
            if not _check_limit(key, platform_limit):
                wait_time = _calculate_wait_time(key, platform_limit)
                request_queue.append((priority, func, args, kwargs))
                logger.warning(f"Requisição enfileirada. Prioridade: {priority.name}")
                return _process_queue()

            return func(*args, **kwargs)
        return wrapper
    return decorator

def _check_limit(key: str, limit: int) -> bool:
    """Verifica se o limite de chamadas foi atingido"""
    current = cache.get(key) or {'count': 0, 'start_time': time.time()}
    
    if time.time() - current['start_time'] > 1:  # Janela de 1 segundo
        current = {'count': 0, 'start_time': time.time()}
    
    if current['count'] >= limit:
        return False
    
    current['count'] += 1
    cache.set(key, current, 1)
    return True

def _calculate_wait_time(key: str, limit: int) -> float:
    """Calcula tempo de espera estimado"""
    current = cache.get(key) or {'count': 0, 'start_time': time.time()}
    elapsed = time.time() - current['start_time']
    return max(0, 1 - elapsed)  # Espera até o próximo segundo

def _process_queue():
    """Processa a fila de requisições por prioridade"""
    if not request_queue:
        return None
        
    # Ordena fila por prioridade
    request_queue = sorted(request_queue, key=lambda x: x[0].value)
    
    # Processa requisição mais prioritária
    priority, func, args, kwargs = request_queue.popleft()
    return func(*args, **kwargs)