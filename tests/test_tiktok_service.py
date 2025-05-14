import pytest
from unittest.mock import patch, MagicMock
from app.services.tiktok_service import TikTokService
from app.schemas.social import TikTokMetricsResponse

class TestTikTokService:
    @pytest.fixture
    def mock_tiktok_service(self):
        with patch('app.utils.api_cache.cache'), \
             patch('app.core.config.settings') as mock_settings:
            mock_settings.TIKTOK_CLIENT_KEY = 'test_key'
            mock_settings.TIKTOK_CLIENT_SECRET = 'test_secret'
            mock_settings.TIKTOK_REFRESH_TOKEN = 'test_refresh'
            yield TikTokService()

    def test_get_tiktok_metrics_success(self, mock_tiktok_service):
        mock_response = {
            'follower_count': 1000,
            'engagement_rate': 0.05,
            'video_views': 5000
        }
        
        with patch.object(mock_tiktok_service, '_make_request', 
                         return_value=mock_response) as mock_request:
            result = mock_tiktok_service.get_tiktok_metrics('test_business')
            
            assert isinstance(result, TikTokMetricsResponse)
            assert result.follower_count == 1000
            mock_request.assert_called_once()

    def test_refresh_token(self, mock_tiktok_service):
        mock_response = {
            'access_token': 'new_token',
            'expires_in': 3600
        }
        
        with patch('requests.post') as mock_post:
            mock_post.return_value.json.return_value = mock_response
            mock_post.return_value.raise_for_status.return_value = None
            
            token = mock_tiktok_service._refresh_access_token()
            assert token == 'new_token'
            mock_post.assert_called_once()

    def test_get_video_analytics(self, mock_tiktok_service):
        mock_response = {'views': 1000, 'likes': 50}
        
        with patch.object(mock_tiktok_service, '_make_request',
                         return_value=mock_response):
            result = mock_tiktok_service.get_video_analytics('video123')
            assert result == mock_response