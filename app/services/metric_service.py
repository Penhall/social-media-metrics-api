from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Optional

from app.db.models import Metric
from app.schemas.metric import MetricCreate, MetricResponse

def create_metric(db: Session, metric: MetricCreate) -> Metric:
    """Cria uma nova entrada de métrica no banco de dados"""
    db_metric = Metric(
        user_id=metric.user_id,
        platform_id=metric.platform_id,
        metric_name=metric.metric_name,
        value=metric.value,
        collected_at=metric.collected_at
    )
    
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_metrics(
    db: Session, 
    user_id: Optional[int] = None,
    platform_id: Optional[int] = None
) -> List[Metric]:
    """Lista métricas com filtros opcionais"""
    query = db.query(Metric)
    
    if user_id:
        query = query.filter(Metric.user_id == user_id)
    if platform_id:
        query = query.filter(Metric.platform_id == platform_id)
        
    return query.order_by(Metric.collected_at.desc()).all()

def calculate_metrics(
    db: Session,
    start_date: str,
    end_date: str,
    metric_name: Optional[str] = None
) -> dict:
    """
    Calcula métricas agregadas por período
    Retorna: {
        "total": int,
        "average": float,
        "min": float,
        "max": float
    }
    """
    query = db.query(Metric).filter(
        Metric.collected_at >= start_date,
        Metric.collected_at <= end_date
    )
    
    if metric_name:
        query = query.filter(Metric.metric_name == metric_name)
        
    metrics = query.all()
    values = [m.value for m in metrics]
    
    return {
        "total": len(values),
        "average": sum(values)/len(values) if values else 0,
        "min": min(values) if values else 0,
        "max": max(values) if values else 0
    }

def get_platform_metrics(
    db: Session,
    platform_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Calcula métricas agregadas por plataforma
    """
    query = db.query(Metric).filter(
        Metric.platform_id == platform_id
    )
    
    if start_date and end_date:
        query = query.filter(
            Metric.collected_at >= start_date,
            Metric.collected_at <= end_date
        )
        
    metrics = query.all()
    return {
        "platform_id": platform_id,
        "total_metrics": len(metrics),
        "unique_users": len({m.user_id for m in metrics}),
        "metric_types": list({m.metric_name for m in metrics})
    }

def get_user_metrics(
    db: Session,
    user_id: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> dict:
    """
    Calcula métricas agregadas por usuário
    """
    query = db.query(Metric).filter(
        Metric.user_id == user_id
    )
    
    if start_date and end_date:
        query = query.filter(
            Metric.collected_at >= start_date,
            Metric.collected_at <= end_date
        )
        
    metrics = query.all()
    return {
        "user_id": user_id,
        "total_metrics": len(metrics),
        "platforms_used": list({m.platform_id for m in metrics}),
        "metric_types": list({m.metric_name for m in metrics})
    }