import pytest
import time
from unittest.mock import patch, MagicMock
from app.utils.rate_limiter import rate_limited, Platform, Priority
from app.utils.api_cache import cache

class TestRateLimiter:
    @patch('app.utils.rate_limiter.cache')
    def test_platform_limits(self, mock_cache):
        """Testa se os limites por plataforma são respeitados"""
        mock_cache.get.return_value = {'count': 0, 'start_time': time.time()}
        
        @rate_limited(Platform.FACEBOOK)
        def mock_facebook_call():
            return "facebook_success"
            
        @rate_limited(Platform.TWITTER) 
        def mock_twitter_call():
            return "twitter_success"
        
        # Primeiras chamadas devem passar
        assert mock_facebook_call() == "facebook_success"
        assert mock_twitter_call() == "twitter_success"
        
        # Simular limite atingido
        mock_cache.get.return_value = {'count': 5, 'start_time': time.time()}
        with pytest.raises(Exception):
            mock_facebook_call()

    @patch('app.utils.rate_limiter.cache')
    def test_priority_queue(self, mock_cache):
        """Testa o sistema de prioridades na fila de espera"""
        mock_cache.get.return_value = {'count': 5, 'start_time': time.time()}
        
        @rate_limited(Platform.INSTAGRAM, Priority.HIGH)
        def high_priority_call():
            return "high_priority"
            
        @rate_limited(Platform.INSTAGRAM, Priority.LOW)
        def low_priority_call():
            return "low_priority"
        
        # Chamadas devem ser enfileiradas
        result = high_priority_call()
        assert "high_priority" in result
        
    @patch('app.utils.rate_limiter.time.sleep')
    def test_wait_time_calculation(self, mock_sleep):
        """Testa o cálculo do tempo de espera"""
        with patch('app.utils.rate_limiter.cache') as mock_cache:
            mock_cache.get.return_value = {
                'count': 5, 
                'start_time': time.time() - 0.5  # 0.5 segundos passados
            }
            
            @rate_limited(Platform.TIKTOK)
            def tiktok_call():
                pass
                
            tiktok_call()
            mock_sleep.assert_called_once()
            sleep_time = mock_sleep.call_args[0][0]
            assert 0.4 < sleep_time < 0.6  # Devia esperar ~0.5s