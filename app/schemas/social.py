from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum

class PlatformType(str, Enum):
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    INSTAGRAM = "instagram"
    WHATSAPP = "whatsapp"

class SocialMediaBase(BaseModel):
    platform: PlatformType
    account_id: str = Field(..., min_length=1, max_length=100)
    timestamp: datetime

class SocialMediaResponse(SocialMediaBase):
    id: str
    metrics: dict
    raw_data: Optional[dict] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TwitterPostSchema(BaseModel):
    tweet_id: str
    text: str
    likes: int
    retweets: int
    replies: int
    url: Optional[HttpUrl] = None

class FacebookPostSchema(BaseModel):
    post_id: str
    message: Optional[str] = None
    likes: int
    comments: int
    shares: int

class InstagramMediaSchema(BaseModel):
    media_id: str
    caption: Optional[str] = None
    likes: int
    comments: int
    media_type: str
    url: HttpUrl

class WhatsAppMessageSchema(BaseModel):
    message_id: str
    from_number: str = Field(..., regex=r"^\+\d{1,15}$")
    timestamp: datetime
    message_type: str
    content: Optional[str] = None

    @validator('from_number')
    def validate_phone_number(cls, v):
        if not v.startswith('+'):
            raise ValueError("Número deve incluir código do país (ex: +55)")
        return v

class SocialBatchRequest(BaseModel):
    platform: PlatformType
    start_date: datetime
    end_date: datetime
    account_ids: List[str] = Field(..., min_items=1)
    metrics: List[str]