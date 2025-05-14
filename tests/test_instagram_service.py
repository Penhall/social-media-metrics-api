import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.instagram_service import InstagramService
from app.schemas.social import SocialMediaResponse, InstagramPostSchema
from requests.exceptions import HTTPError
import base64

@pytest.fixture
def instagram_service():
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.INSTAGRAM_APP_ID = 'test_id'
        mock_settings.INSTAGRAM_APP_SECRET = 'test_secret'
        mock_settings.FACEBOOK_ACCESS_TOKEN = 'test_token'
        yield InstagramService()

def test_get_instagram_metrics_success(instagram_service):
    # Mock da resposta da API
    mock_response = {
        'followers_count': 1500,
        'follows_count': 300,
        'media_count': 50,
        'media': {
            'data': [
                {
                    'id': 'post1',
                    'caption': 'Test post',
                    'like_count': 100,
                    'comments_count': 20,
                    'timestamp': '2023-01-01T00:00:00+0000',
                    'permalink': 'https://instagram.com/p/post1'
                }
            ]
        }
    }
    
    with patch.object(instagram_service, '_make_request') as mock_request:
        mock_request.return_value = mock_response
        
        result = instagram_service.get_instagram_metrics('123')
        
        assert isinstance(result, SocialMediaResponse)
        assert result.platform == 'instagram'
        assert result.metrics['followers'] == 1500
        assert len(result.metrics['recent_posts']) == 1
        assert isinstance(result.timestamp, datetime)

def test_get_instagram_metrics_invalid_token(instagram_service):
    # Mock de erro 400 (token inválido)
    mock_error = HTTPError()
    mock_error.response = Mock(status_code=400)
    
    with patch.object(instagram_service, '_make_request') as mock_request:
        mock_request.side_effect = mock_error
        
        with pytest.raises(HTTPError):
            instagram_service.get_instagram_metrics('123')

def test_instagram_post_schema_validation():
    # Teste de validação do schema
    valid_post = {
        'post_id': '123',
        'caption': 'Test post',
        'likes': 100,
        'comments': 20,
        'timestamp': '2023-01-01T00:00:00+0000',
        'url': 'https://instagram.com/p/123'
    }
    
    assert InstagramPostSchema(**valid_post)

def test_auth_setup(instagram_service):
    # Teste de configuração de autenticação
    assert instagram_service.basic_auth == base64.b64encode(b'test_id:test_secret').decode()

def test_empty_media_handling(instagram_service):
    # Teste para conta sem posts
    mock_response = {
        'followers_count': 1500,
        'follows_count': 300,
        'media_count': 0,
        'media': {'data': []}
    }
    
    with patch.object(instagram_service, '_make_request') as mock_request:
        mock_request.return_value = mock_response
        
        result = instagram_service.get_instagram_metrics('123')
        assert len(result.metrics['recent_posts']) == 0