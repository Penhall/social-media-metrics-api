import pytest
from unittest.mock import patch, MagicMock
import asyncio
from app.utils.retry import retry_request, BackoffStrategy, CircuitBreaker
from fastapi import HTTPException
import httpx
import logging

class TestRetryMechanism:
    @patch('app.utils.retry.time.sleep')
    async def test_exponential_backoff(self, mock_sleep):
        """Testa estratégia de backoff exponencial"""
        mock_func = MagicMock(side_effect=HTTPException(status_code=503))
        
        @retry_request(
            max_retries=3,
            strategy=BackoffStrategy.EXPONENTIAL,
            log_level=logging.INFO
        )
        async def test_func():
            return await mock_func()
            
        with pytest.raises(HTTPException):
            await test_func()
            
        assert mock_func.call_count == 4  # 1 chamada inicial + 3 retentativas
        assert mock_sleep.call_count == 3

    async def test_circuit_breaker(self):
        """Testa abertura do circuit breaker"""
        cb = CircuitBreaker(max_failures=2, reset_timeout=1)
        
        # Simular falhas consecutivas
        for _ in range(2):
            cb.record_failure()
            
        assert cb.is_open is True
        
        # Verificar se resetou após timeout
        with patch('time.time', return_value=time.time() + 2):
            assert cb.check_state() is True
            assert cb.is_open is False

    @pytest.mark.parametrize("strategy,expected_delays", [
        (BackoffStrategy.LINEAR, [1, 2, 3]),
        (BackoffStrategy.CONSTANT, [1, 1, 1]),
        (BackoffStrategy.FIBONACCI, [1, 2, 3]),
    ])
    async def test_backoff_strategies(self, strategy, expected_delays):
        """Testa diferentes estratégias de backoff"""
        mock_func = MagicMock(side_effect=HTTPException(status_code=503))
        
        @retry_request(
            max_retries=3,
            initial_delay=1,
            strategy=strategy
        )
        async def test_func():
            return await mock_func()
            
        with patch('asyncio.sleep') as mock_sleep:
            with pytest.raises(HTTPException):
                await test_func()
                
            # Verifica os delays aplicados
            actual_delays = [call[0][0] for call in mock_sleep.call_args_list]
            for actual, expected in zip(actual_delays, expected_delays):
                assert abs(actual - expected) < 0.2  # Permite pequena variação do jitter

    async def test_log_level_control(self):
        """Testa controle de nível de log"""
        with patch('logging.Logger.log') as mock_log:
            mock_func = MagicMock(side_effect=HTTPException(status_code=503))
            
            @retry_request(
                max_retries=1,
                log_level=logging.DEBUG
            )
            async def test_func():
                return await mock_func()
                
            with pytest.raises(HTTPException):
                await test_func()
                
            # Verifica se usou o nível de log correto
            assert mock_log.call_args[0][0] == logging.DEBUG