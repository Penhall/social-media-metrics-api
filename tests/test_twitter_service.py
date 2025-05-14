import pytest
from unittest.mock import Mock, patch
from datetime import datetime
from app.services.twitter_service import TwitterService
from app.schemas.social import SocialMediaResponse, TwitterPostSchema
from requests.exceptions import HTTPError

@pytest.fixture
def mock_oauth():
    with patch('requests_oauthlib.OAuth2Session') as mock:
        mock_instance = Mock()
        mock_instance.token = {'access_token': 'test_token'}
        mock_instance.fetch_token.return_value = {'access_token': 'new_token'}
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def twitter_service(mock_oauth):
    return TwitterService()

def test_get_twitter_metrics_success(twitter_service, mock_oauth):
    # Mock das respostas da API
    mock_response_user = {
        'data': {
            'id': '123',
            'public_metrics': {
                'followers_count': 1000,
                'following_count': 500,
                'tweet_count': 200
            }
        }
    }
    
    mock_response_tweets = {
        'data': [
            {
                'id': 'tweet1',
                'text': 'Test tweet',
                'public_metrics': {
                    'like_count': 10,
                    'retweet_count': 5,
                    'reply_count': 3
                },
                'created_at': '2023-01-01T00:00:00Z'
            }
        ]
    }
    
    with patch.object(twitter_service, '_make_request') as mock_request:
        mock_request.side_effect = [mock_response_user, mock_response_tweets]
        
        result = twitter_service.get_twitter_metrics('123')
        
        assert isinstance(result, SocialMediaResponse)
        assert result.platform == 'twitter'
        assert result.metrics['followers'] == 1000
        assert len(result.metrics['recent_tweets']) == 1
        assert isinstance(result.timestamp, datetime)

def test_get_twitter_metrics_unauthorized(twitter_service, mock_oauth):
    # Mock de erro 401
    mock_error = HTTPError()
    mock_error.response = Mock(status_code=401)
    
    with patch.object(twitter_service, '_make_request') as mock_request:
        mock_request.side_effect = [mock_error, mock_error]
        
        # Primeira chamada deve falhar e tentar renovar token
        with pytest.raises(HTTPError):
            twitter_service.get_twitter_metrics('123')
        
        assert mock_oauth.fetch_token.called

def test_twitter_post_schema_validation(twitter_service):
    # Teste de validação do schema
    valid_tweet = {
        'tweet_id': '123',
        'text': 'Test tweet',
        'likes': 10,
        'retweets': 5,
        'replies': 3,
        'url': 'https://twitter.com/user/status/123'
    }
    
    assert TwitterPostSchema(**valid_tweet)

    # Teste com dados inválidos
    invalid_tweet = {
        'tweet_id': '123',
        'likes': 'not_an_integer',  # Valor inválido
        'retweets': 5
    }
    
    with pytest.raises(ValueError):
        TwitterPostSchema(**invalid_tweet)

def test_refresh_token(twitter_service, mock_oauth):
    # Teste de renovação de token
    twitter_service.oauth.token = None
    twitter_service._refresh_token()
    
    assert twitter_service.oauth.token == {'access_token': 'new_token'}
    assert mock_oauth.fetch_token.called