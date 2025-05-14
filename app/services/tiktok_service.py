from typing import Dict, Any
from app.core.social_api import SocialAPI
from app.schemas.social import TikTokMetricsResponse
from app.utils.retry import retry_on_failure

class TikTokService(SocialAPI):
    """Serviço para integração com a TikTok Business API"""
    
    def __init__(self):
        super().__init__(platform='tiktok')
        self.headers.update({
            'Authorization': f'Bearer {self._get_access_token()}'
        })
    
    def _get_access_token(self) -> str:
        """Obtém token de acesso OAuth2, renovando se expirado"""
        from app.core.config import settings
        from app.utils.api_cache import cache
        
        cached_token = cache.get('tiktok_access_token')
        if cached_token:
            return cached_token
            
        return self._refresh_access_token()

    def _refresh_access_token(self) -> str:
        """Renova o token de acesso usando refresh token"""
        from app.core.config import settings
        from app.utils.api_cache import cache
        import requests
        
        if not settings.TIKTOK_REFRESH_TOKEN:
            raise ValueError("Refresh token não configurado")
            
        auth_url = "https://open.tiktokapis.com/v2/oauth/token/"
        payload = {
            'client_key': settings.TIKTOK_CLIENT_KEY,
            'client_secret': settings.TIKTOK_CLIENT_SECRET,
            'refresh_token': settings.TIKTOK_REFRESH_TOKEN,
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(auth_url, data=payload)
        response.raise_for_status()
        token_data = response.json()
        
        # Armazena novo token em cache
        cache.set('tiktok_access_token',
                 token_data['access_token'],
                 timeout=token_data['expires_in'] - 60)  # 1 min de margem
        
        return token_data['access_token']
    
    @retry_on_failure(max_retries=3)
    def get_tiktok_metrics(self, business_id: str) -> TikTokMetricsResponse:
        """Obtém métricas de negócios da API do TikTok
        
        Args:
            business_id: ID da conta de negócios no TikTok
            
        Returns:
            TikTokMetricsResponse: Modelo Pydantic com as métricas
        """
        endpoint = f'business/{business_id}/metrics'
        params = {
            'metrics': 'follower_count,engagement_rate,video_views',
            'period': 'last_30_days'
        }
        
        data = self._make_request(endpoint, params)
        return TikTokMetricsResponse(**data)

    def get_video_analytics(self, video_id: str) -> Dict[str, Any]:
        """Obtém análises detalhadas de um vídeo específico"""
        endpoint = f'video/{video_id}/analytics'
        return self._make_request(endpoint)