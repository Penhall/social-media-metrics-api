import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.facebook_service import FacebookService
from app.schemas.social import SocialMediaResponse, FacebookPostSchema
from requests.exceptions import HTTPError

@pytest.fixture
def facebook_service():
    with patch('app.core.config.settings') as mock_settings:
        mock_settings.FACEBOOK_ACCESS_TOKEN = 'test_token'
        yield FacebookService()

def test_get_facebook_metrics_success(facebook_service):
    # Mock da resposta da API
    mock_response = {
        'fan_count': 1000,
        'followers_count': 800,
        'posts': {
            'data': [
                {
                    'id': 'post1',
                    'message': 'Test post',
                    'created_time': '2023-01-01T00:00:00+0000',
                    'shares': {'count': 10},
                    'comments': {'summary': {'total_count': 5}},
                    'reactions': {'summary': {'total_count': 20}}
                }
            ]
        }
    }
    
    with patch.object(facebook_service, '_make_request') as mock_request:
        mock_request.return_value = mock_response
        
        result = facebook_service.get_facebook_metrics('123')
        
        assert isinstance(result, SocialMediaResponse)
        assert result.platform == 'facebook'
        assert result.metrics['fan_count'] == 1000
        assert len(result.metrics['recent_posts']) == 1
        assert isinstance(result.timestamp, datetime)

def test_get_facebook_metrics_invalid_token(facebook_service):
    # Mock de erro 400 (token inválido)
    mock_error = HTTPError()
    mock_error.response = Mock(status_code=400)
    
    with patch.object(facebook_service, '_make_request') as mock_request:
        mock_request.side_effect = mock_error
        
        with pytest.raises(HTTPError):
            facebook_service.get_facebook_metrics('123')

def test_facebook_post_schema_validation():
    # Teste de validação do schema
    valid_post = {
        'post_id': '123',
        'message': 'Test post',
        'created_time': '2023-01-01T00:00:00+0000',
        'shares': 10,
        'comments': 5,
        'reactions': 20,
        'url': 'https://facebook.com/123'
    }
    
    assert FacebookPostSchema(**valid_post)

    # Teste com dados inválidos
    invalid_post = {
        'post_id': '123',
        'shares': 'not_an_integer'  # Valor inválido
    }
    
    with pytest.raises(ValueError):
        FacebookPostSchema(**invalid_post)

def test_empty_posts_handling(facebook_service):
    # Teste para página sem posts
    mock_response = {
        'fan_count': 1000,
        'followers_count': 800,
        'posts': {'data': []}
    }
    
    with patch.object(facebook_service, '_make_request') as mock_request:
        mock_request.return_value = mock_response
        
        result = facebook_service.get_facebook_metrics('123')
        assert len(result.metrics['recent_posts']) == 0