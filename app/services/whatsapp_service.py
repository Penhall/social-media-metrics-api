from typing import Dict, Optional
from fastapi import HTTPException
from app.core.config import settings
from app.utils.api_utils import make_api_request
from app.schemas.social import WhatsAppMetrics

class WhatsAppService:
    def __init__(self):
        self.base_url = settings.WHATSAPP_API_URL
        self.headers = {
            "Authorization": f"Bearer {settings.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json"
        }

    async def get_whatsapp_metrics(self, business_id: str) -> WhatsAppMetrics:
        """Obtém métricas da conta WhatsApp Business"""
        url = f"{self.base_url}/{business_id}/metrics"
        try:
            response = await make_api_request(
                url=url,
                method="GET",
                headers=self.headers
            )
            return WhatsAppMetrics(**response)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao buscar métricas do WhatsApp: {str(e)}"
            )

    async def setup_webhooks(self, callback_url: str) -> bool:
        """Configura webhooks para receber mensagens"""
        url = f"{self.base_url}/webhooks"
        payload = {
            "url": callback_url,
            "events": ["messages", "status"]
        }
        try:
            await make_api_request(
                url=url,
                method="POST",
                headers=self.headers,
                json_data=payload
            )
            return True
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Erro ao configurar webhooks: {str(e)}"
            )