from pydantic import BaseSettings, PostgresDsn

class TestSettings(BaseSettings):
    class Config:
        arbitrary_types_allowed = True
        
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    DATABASE_URL: str = "sqlite:///:memory:"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "test"
    POSTGRES_PASSWORD: str = "test"
    POSTGRES_DB: str = "test"
    
    # API Keys
    TWITTER_API_KEY: str = "test_twitter_key"
    TWITTER_API_SECRET: str = "test_twitter_secret"
    FACEBOOK_APP_ID: str = "test_fb_id"
    FACEBOOK_APP_SECRET: str = "test_fb_secret"
    INSTAGRAM_APP_ID: str = "test_ig_id"
    INSTAGRAM_APP_SECRET: str = "test_ig_secret"
    WHATSAPP_BUSINESS_ID: str = "test_wa_business"
    WHATSAPP_ACCESS_TOKEN: str = "test_wa_token"
    
    # General settings
    SECRET_KEY: str = "test_secret_key"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    BACKEND_CORS_ORIGINS: str = "*"
    ALGORITHM: str = "HS256"

def get_test_settings():
    """Retorna configurações de teste mockadas"""
    return TestSettings()