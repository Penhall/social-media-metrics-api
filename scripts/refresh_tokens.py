import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests
from app.core.config import settings
from app.db.crud import update_user_tokens
from app.db.database import get_db
from app.schemas.social import TokenRefreshResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TokenRefresher:
    def __init__(self):
        self.db = next(get_db())
        
    def refresh_twitter_token(self, refresh_token: str) -> Optional[Dict]:
        """Refresh Twitter OAuth2 token"""
        try:
            response = requests.post(
                "https://api.twitter.com/2/oauth2/token",
                data={
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                    "client_id": settings.TWITTER_CLIENT_ID
                },
                auth=(settings.TWITTER_CLIENT_ID, settings.TWITTER_CLIENT_SECRET)
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Twitter token refresh failed: {str(e)}")
            return None

    def refresh_all_tokens(self):
        """Refresh all expired or soon-to-expire tokens"""
        users = self.db.query(User).filter(
            User.token_expires_at < datetime.utcnow() + timedelta(hours=1)
        ).all()
        
        for user in users:
            platform = user.platform
            refresh_token = user.refresh_token
            
            if platform == "twitter":
                new_tokens = self.refresh_twitter_token(refresh_token)
            # Adicionar outros platforms aqui
            
            if new_tokens:
                update_user_tokens(
                    self.db,
                    user.id,
                    new_tokens["access_token"],
                    new_tokens["refresh_token"],
                    datetime.utcnow() + timedelta(seconds=new_tokens["expires_in"])
                )
                logger.info(f"Tokens atualizados para usuário {user.id}")

if __name__ == "__main__":
    refresher = TokenRefresher()
    refresher.refresh_all_tokens()