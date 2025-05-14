import logging
from typing import Dict, Any
from datetime import datetime
import requests
from app.core.social_api import SocialAPI
from app.core.config import settings
from app.schemas.social import FacebookPostSchema, PlatformType, SocialMediaResponse
from app.utils.api_cache import cache

logger = logging.getLogger(__name__)

class FacebookService(SocialAPI):
    """Serviço para integração com Facebook Graph API"""
    
    def __init__(self):
        super().__init__(api_name="facebook")
        self.base_url = "https://graph.facebook.com/v18.0"
        self.access_token = settings.FACEBOOK_ACCESS_TOKEN
        
    def get_facebook_metrics(self, page_id: str) -> SocialMediaResponse:
        """Obtém métricas de uma página do Facebook"""
        try:
            # Obtém informações básicas da página
            page_data = self._make_request(
                method="GET",
                endpoint=f"/{page_id}",
                params={
                    "fields": "fan_count,followers_count,posts.limit(10){created_time,message,shares,comments.limit(1).summary(true),reactions.limit(1).summary(true)}",
                    "access_token": self.access_token
                }
            )
            
            # Processa métricas
            fan_count = page_data.get('fan_count', 0)
            followers_count = page_data.get('followers_count', 0)
            
            recent_posts = []
            for post in page_data.get('posts', {}).get('data', []):
                try:
                    recent_posts.append(
                        FacebookPostSchema(
                            post_id=post['id'],
                            message=post.get('message', ''),
                            created_time=post.get('created_time'),
                            shares=post.get('shares', {}).get('count', 0),
                            comments=post.get('comments', {}).get('summary', {}).get('total_count', 0),
                            reactions=post.get('reactions', {}).get('summary', {}).get('total_count', 0),
                            url=f"https://facebook.com/{post['id']}"
                        ).dict()
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(f"Erro ao processar post {post.get('id')}: {str(e)}")
            
            metrics_data = {
                "platform": PlatformType.FACEBOOK,
                "account_id": page_id,
                "timestamp": datetime.utcnow(),
                "metrics": {
                    "fan_count": fan_count,
                    "followers_count": followers_count,
                    "recent_posts": recent_posts
                },
                "raw_data": page_data
            }
            
            return SocialMediaResponse(**metrics_data)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.error(f"Token de acesso inválido ou expirado: {str(e)}")
            logger.error(f"Erro na API Facebook: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise