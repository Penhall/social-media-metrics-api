from datetime import datetime
from pydantic import BaseModel

class MetricBase(BaseModel):
    user_id: int
    platform_id: int
    metric_name: str
    value: float
    collected_at: datetime

class MetricCreate(MetricBase):
    pass

class MetricResponse(MetricBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True