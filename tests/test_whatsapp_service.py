import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.services.whatsapp_service import WhatsAppService
from app.schemas.social import WhatsAppMetrics

@pytest.fixture
def whatsapp_service():
    return WhatsAppService()

@pytest.mark.asyncio
async def test_get_whatsapp_metrics_success(whatsapp_service):
    mock_response = {
        "messages_sent": 100,
        "messages_received": 150,
        "delivered_rate": 0.98
    }
    
    with patch("app.utils.api_utils.make_api_request", 
               new_callable=AsyncMock) as mock_request:
        mock_request.return_value = mock_response
        
        result = await whatsapp_service.get_whatsapp_metrics("test_business")
        assert isinstance(result, WhatsAppMetrics)
        assert result.messages_sent == 100

@pytest.mark.asyncio
async def test_get_whatsapp_metrics_failure(whatsapp_service):
    with patch("app.utils.api_utils.make_api_request", 
               new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("API Error")
        
        with pytest.raises(HTTPException) as exc_info:
            await whatsapp_service.get_whatsapp_metrics("test_business")
        assert exc_info.value.status_code == 500

@pytest.mark.asyncio
async def test_setup_webhooks_success(whatsapp_service):
    with patch("app.utils.api_utils.make_api_request", 
               new_callable=AsyncMock) as mock_request:
        mock_request.return_value = {}
        
        result = await whatsapp_service.setup_webhooks("https://callback.test")
        assert result is True

@pytest.mark.asyncio
async def test_setup_webhooks_failure(whatsapp_service):
    with patch("app.utils.api_utils.make_api_request", 
               new_callable=AsyncMock) as mock_request:
        mock_request.side_effect = Exception("Webhook Error")
        
        with pytest.raises(HTTPException) as exc_info:
            await whatsapp_service.setup_webhooks("https://callback.test")
        assert exc_info.value.status_code == 500