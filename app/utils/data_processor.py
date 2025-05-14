from typing import Dict, Any
from pydantic import BaseModel, validator
from datetime import datetime
from app.schemas.social import SocialMetricBase

class NormalizedMetric(BaseModel):
    """Schema comum para métricas normalizadas"""
    platform: str
    metric_type: str
    value: float
    date: datetime
    page_id: str
    username: str
    engagement_rate: float = None
    
    @validator('value')
    def validate_positive(cls, v):
        if v < 0:
            raise ValueError("Metric value must be positive")
        return v

class DataProcessor:
    def __init__(self):
        self.transformers = {
            'facebook': self.transform_facebook,
            'twitter': self.transform_twitter,
            'instagram': self.transform_instagram,
            'tiktok': self.transform_tiktok
        }

    def transform_facebook(self, raw_data: Dict[str, Any]) -> NormalizedMetric:
        """Transforma dados brutos do Facebook para formato normalizado"""
        return NormalizedMetric(
            platform='facebook',
            metric_type=raw_data['name'],
            value=float(raw_data['values'][0]['value']),
            date=datetime.strptime(raw_data['end_time'], '%Y-%m-%dT%H:%M:%S%z'),
            page_id=raw_data['id'],
            username=raw_data.get('page_name', ''),
            engagement_rate=self._calc_engagement(raw_data)
        )

    def transform_twitter(self, raw_data: Dict[str, Any]) -> NormalizedMetric:
        """Transforma dados brutos do Twitter para formato normalizado"""
        return NormalizedMetric(
            platform='twitter',
            metric_type=raw_data['metric_name'],
            value=float(raw_data['metric_value']),
            date=datetime.strptime(raw_data['date'], '%Y-%m-%d'),
            page_id=raw_data['account_id'],
            username=raw_data.get('username', ''),
            engagement_rate=self._calc_engagement(raw_data)
        )

    def _calc_engagement(self, data: Dict[str, Any]) -> float:
        """Calcula taxa de engajamento genérica"""
        # Implementação básica - pode ser sobrescrita por plataforma
        impressions = data.get('impressions', 1)
        engagements = data.get('engagements', 0)
        return (engagements / impressions) * 100 if impressions else 0

    def process(self, platform: str, raw_data: Dict[str, Any]) -> NormalizedMetric:
        """Processa dados brutos de qualquer plataforma"""
        transformer = self.transformers.get(platform)
        if not transformer:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return transformer(raw_data)