import logging
from typing import Dict, Any
from datetime import datetime
import requests
import base64
from app.core.social_api import SocialAPI
from app.core.config import settings
from app.schemas.social import InstagramPostSchema, PlatformType, SocialMediaResponse
from app.utils.api_cache import cache

logger = logging.getLogger(__name__)

class InstagramService(SocialAPI):
    """Serviço para integração com Instagram Graph API"""
    
    def __init__(self):
        super().__init__(api_name="instagram")
        self.base_url = "https://graph.facebook.com/v18.0"
        self._setup_auth()
        
    def _setup_auth(self):
        """Configura autenticação básica"""
        credentials = f"{settings.INSTAGRAM_APP_ID}:{settings.INSTAGRAM_APP_SECRET}"
        self.basic_auth = base64.b64encode(credentials.encode()).decode()
        
    def get_instagram_metrics(self, account_id: str) -> SocialMediaResponse:
        """Obtém métricas de uma conta do Instagram"""
        try:
            # Obtém informações básicas da conta
            account_data = self._make_request(
                method="GET",
                endpoint=f"/{account_id}",
                params={
                    "fields": "followers_count,follows_count,media_count,media.limit(10){caption,like_count,comments_count,timestamp,permalink}",
                    "access_token": settings.FACEBOOK_ACCESS_TOKEN  # Instagram usa token do Facebook
                },
                headers={
                    "Authorization": f"Basic {self.basic_auth}"
                }
            )
            
            # Processa métricas
            followers = account_data.get('followers_count', 0)
            follows = account_data.get('follows_count', 0)
            media_count = account_data.get('media_count', 0)
            
            recent_posts = []
            for media in account_data.get('media', {}).get('data', []):
                try:
                    recent_posts.append(
                        InstagramPostSchema(
                            post_id=media['id'],
                            caption=media.get('caption', ''),
                            likes=media.get('like_count', 0),
                            comments=media.get('comments_count', 0),
                            timestamp=media.get('timestamp'),
                            url=media.get('permalink')
                        ).dict()
                    )
                except (KeyError, ValueError) as e:
                    logger.warning(f"Erro ao processar post {media.get('id')}: {str(e)}")
            
            metrics_data = {
                "platform": PlatformType.INSTAGRAM,
                "account_id": account_id,
                "timestamp": datetime.utcnow(),
                "metrics": {
                    "followers": followers,
                    "following": follows,
                    "media_count": media_count,
                    "recent_posts": recent_posts
                },
                "raw_data": account_data
            }
            
            return SocialMediaResponse(**metrics_data)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 400:
                logger.error(f"Token de acesso inválido ou expirado: {str(e)}")
            logger.error(f"Erro na API Instagram: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise