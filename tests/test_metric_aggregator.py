import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.services.metric_aggregator import MetricAggregator
from app.schemas.metric import SocialMetrics

@pytest.fixture
def aggregator():
    return MetricAggregator()

@pytest.mark.asyncio
async def test_get_all_metrics_success(aggregator):
    mock_data = {
        "engagement": 0.5,
        "reach": 1000,
        "impressions": 1500,
        "interactions": 500
    }
    
    with patch("app.services.facebook_service.FacebookService.get_metrics",
               new_callable=AsyncMock) as mock_fb, \
         patch("app.services.instagram_service.InstagramService.get_metrics",
               new_callable=AsyncMock) as mock_ig, \
         patch("app.services.twitter_service.TwitterService.get_metrics",
               new_callable=AsyncMock) as mock_tw, \
         patch("app.services.whatsapp_service.WhatsAppService.get_whatsapp_metrics",
               new_callable=AsyncMock) as mock_wa:
        
        mock_fb.return_value = mock_data
        mock_ig.return_value = mock_data
        mock_tw.return_value = mock_data
        mock_wa.return_value = {"messages_sent": 100, "messages_received": 150}
        
        result = await aggregator.get_all_metrics()
        assert isinstance(result, SocialMetrics)
        assert "facebook" in result.platforms
        assert "whatsapp" in result.platforms

@pytest.mark.asyncio
async def test_get_all_metrics_with_platform_filter(aggregator):
    mock_data = {"engagement": 0.5, "reach": 1000}
    
    with patch("app.services.facebook_service.FacebookService.get_metrics",
               new_callable=AsyncMock) as mock_fb:
        mock_fb.return_value = mock_data
        
        result = await aggregator.get_all_metrics(platforms=["facebook"])
        assert list(result.platforms.keys()) == ["facebook"]

@pytest.mark.asyncio
async def test_normalization_logic(aggregator):
    mock_data = {"engagement_rate": 0.5, "reach": 1000}
    
    with patch("app.services.facebook_service.FacebookService.get_metrics",
               new_callable=AsyncMock) as mock_fb:
        mock_fb.return_value = mock_data
        
        result = await aggregator.get_all_metrics(platforms=["facebook"])
        assert "engagement" in result.platforms["facebook"]
        assert result.platforms["facebook"]["engagement"] == 0.5

@pytest.mark.asyncio
async def test_service_failure_handling(aggregator):
    with patch("app.services.facebook_service.FacebookService.get_metrics",
               new_callable=AsyncMock) as mock_fb:
        mock_fb.side_effect = Exception("API Error")
        
        with pytest.raises(HTTPException) as exc_info:
            await aggregator.get_all_metrics(platforms=["facebook"])
        assert exc_info.value.status_code == 500