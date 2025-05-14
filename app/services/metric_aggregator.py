from typing import Dict, List
from datetime import datetime, timedelta
from fastapi import HTTPException
from app.services.facebook_service import FacebookService
from app.services.instagram_service import InstagramService
from app.services.twitter_service import TwitterService
from app.services.whatsapp_service import WhatsAppService
from app.schemas.metric import SocialMetrics, PlatformMetrics
from app.utils.date_utils import get_date_range

class MetricAggregator:
    def __init__(self):
        self.services = {
            "facebook": FacebookService(),
            "instagram": InstagramService(),
            "twitter": TwitterService(),
            "whatsapp": WhatsAppService()
        }

    async def get_all_metrics(self, 
                            platforms: List[str] = None,
                            date_from: datetime = None,
                            date_to: datetime = None) -> SocialMetrics:
        """Consolida métricas de todas as plataformas"""
        if not date_from or not date_to:
            date_from, date_to = get_date_range(days=7)
            
        if not platforms:
            platforms = list(self.services.keys())

        results = {}
        for platform in platforms:
            if platform not in self.services:
                continue
                
            try:
                metrics = await self._get_platform_metrics(
                    platform, 
                    date_from, 
                    date_to
                )
                results[platform] = self._normalize_metrics(platform, metrics)
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Erro ao buscar métricas de {platform}: {str(e)}"
                )

        return SocialMetrics(
            platforms=results,
            date_from=date_from,
            date_to=date_to
        )

    async def _get_platform_metrics(self, 
                                  platform: str,
                                  date_from: datetime,
                                  date_to: datetime) -> PlatformMetrics:
        """Obtém métricas de uma plataforma específica"""
        service = self.services[platform]
        return await service.get_metrics(date_from, date_to)

    def _normalize_metrics(self, 
                         platform: str,
                         metrics: PlatformMetrics) -> Dict:
        """Normaliza métricas entre diferentes plataformas"""
        normalized = {
            "engagement": metrics.engagement_rate,
            "reach": metrics.reach,
            "impressions": metrics.impressions,
            "interactions": metrics.interactions
        }
        
        # WhatsApp tem métricas diferentes
        if platform == "whatsapp":
            normalized.update({
                "messages_sent": metrics.messages_sent,
                "messages_received": metrics.messages_received
            })
            
        return normalized