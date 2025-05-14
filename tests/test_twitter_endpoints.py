import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.social import TwitterUserMetrics, TwitterPostMetrics

client = TestClient(app)

def test_get_twitter_user_metrics_success(mocker):
    """Testa obtenção bem-sucedida de métricas de usuário"""
    mock_data = {
        "data": {
            "id": "123",
            "username": "testuser",
            "name": "Test User",
            "created_at": "2020-01-01T00:00:00Z",
            "public_metrics": {
                "followers_count": 100,
                "following_count": 50,
                "tweet_count": 200,
                "listed_count": 5
            }
        }
    }
    
    mocker.patch(
        "app.services.twitter_service.TwitterService.get_user_metrics",
        return_value=mock_data
    )
    
    response = client.get("/api/v1/metrics/twitter/testuser")
    assert response.status_code == 200
    assert TwitterUserMetrics(**response.json())

def test_get_twitter_user_not_found(mocker):
    """Testa erro quando usuário não existe"""
    mocker.patch(
        "app.services.twitter_service.TwitterService.get_user_metrics",
        side_effect=Exception("User not found")
    )
    
    response = client.get("/api/v1/metrics/twitter/invaliduser")
    assert response.status_code == 400
    assert "User not found" in response.json()["detail"]

def test_get_twitter_tweet_metrics_success(mocker):
    """Testa obtenção bem-sucedida de métricas de tweet"""
    mock_data = {
        "data": {
            "id": "456",
            "text": "Test tweet",
            "created_at": "2021-01-01T00:00:00Z",
            "public_metrics": {
                "retweet_count": 10,
                "reply_count": 5,
                "like_count": 20,
                "quote_count": 2,
                "impression_count": 100
            }
        }
    }
    
    mocker.patch(
        "app.services.twitter_service.TwitterService.get_tweet_metrics",
        return_value=mock_data
    )
    
    response = client.get("/api/v1/metrics/twitter/tweets/456")
    assert response.status_code == 200
    assert TwitterPostMetrics(**response.json())

@pytest.mark.asyncio
async def test_rate_limiting(mocker):
    """Testa se o rate limiting está sendo aplicado"""
    from app.services.twitter_service import TwitterService
    
    service = TwitterService()
    with pytest.raises(Exception):
        # Tenta fazer mais chamadas que o limite permitido
        for _ in range(350):
            await service.get_user_metrics("testuser")