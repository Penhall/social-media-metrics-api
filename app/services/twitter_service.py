import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import requests
from requests_oauthlib import OAuth2Session
from pydantic import ValidationError
from app.core.social_api import SocialAPI
from app.core.config import settings
from app.schemas.social import TwitterPostSchema, PlatformType, SocialMediaResponse
from app.utils.api_cache import cache

logger = logging.getLogger(__name__)

class TwitterService(SocialAPI):
    """Serviço para integração com Twitter API v2 usando OAuth2"""
    
    def __init__(self):
        super().__init__(api_name="twitter")
        self.base_url = "https://api.twitter.com/2"
        self._setup_oauth()
        
    def _setup_oauth(self):
        """Configura autenticação OAuth2"""
        self.oauth = OAuth2Session(
            client_id=settings.TWITTER_API_KEY,
            scope=["tweet.read", "users.read"]
        )
        
        # Tenta obter token do cache
        cached_token = cache.get('twitter_oauth_token')
        if cached_token:
            self.oauth.token = cached_token
        else:
            self._refresh_token()
    
    def _refresh_token(self):
        """Obtém novo token OAuth2"""
        try:
            token = self.oauth.fetch_token(
                token_url='https://api.twitter.com/2/oauth2/token',
                client_secret=settings.TWITTER_API_SECRET,
                include_client_id=True
            )
            cache.set('twitter_oauth_token', token, timeout=3600)  # 1 hora
            return token
        except Exception as e:
            logger.error(f"Erro ao obter token OAuth2: {str(e)}")
            raise
    
    def get_twitter_metrics(self, account_id: str) -> SocialMediaResponse:
        """Obtém métricas de uma conta do Twitter"""
        try:
            # Obtém informações do usuário
            user_data = self._make_request(
                method="GET",
                endpoint=f"/users/{account_id}",
                params={"user.fields": "public_metrics"}
            )
            
            # Obtém tweets recentes
            tweets_data = self._make_request(
                method="GET",
                endpoint=f"/users/{account_id}/tweets",
                params={
                    "tweet.fields": "public_metrics,created_at",
                    "max_results": 10
                }
            )
            
            # Processa métricas
            user_metrics = user_data.get('data', {}).get('public_metrics', {})
            tweets = tweets_data.get('data', [])
            
            recent_tweets = []
            for tweet in tweets:
                try:
                    recent_tweets.append(
                        TwitterPostSchema(
                            tweet_id=tweet['id'],
                            text=tweet.get('text', ''),
                            likes=tweet['public_metrics'].get('like_count', 0),
                            retweets=tweet['public_metrics'].get('retweet_count', 0),
                            replies=tweet['public_metrics'].get('reply_count', 0),
                            url=f"https://twitter.com/user/status/{tweet['id']}"
                        ).dict()
                    )
                except (KeyError, ValidationError) as e:
                    logger.warning(f"Erro ao processar tweet {tweet.get('id')}: {str(e)}")
            
            metrics_data = {
                "platform": PlatformType.TWITTER,
                "account_id": account_id,
                "timestamp": datetime.utcnow(),
                "metrics": {
                    "followers": user_metrics.get('followers_count', 0),
                    "following": user_metrics.get('following_count', 0),
                    "tweet_count": user_metrics.get('tweet_count', 0),
                    "recent_tweets": recent_tweets
                },
                "raw_data": {
                    "user": user_data,
                    "tweets": tweets_data
                }
            }
            
            return SocialMediaResponse(**metrics_data)
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                # Token expirado, tenta renovar
                self._refresh_token()
                return self.get_twitter_metrics(account_id)
            logger.error(f"Erro na API Twitter: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            raise

    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Sobrescreve método para incluir OAuth"""
        headers = kwargs.get('headers', {})
        headers['Authorization'] = f"Bearer {self.oauth.token['access_token']}"
        kwargs['headers'] = headers
        
        return super()._make_request(method, endpoint, **kwargs)