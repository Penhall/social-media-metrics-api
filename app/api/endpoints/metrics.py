from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import Metric
from app.schemas.metric import MetricCreate, MetricResponse
from app.services.metric_service import create_metric, get_metrics

router = APIRouter()

@router.post("/metrics", response_model=MetricResponse, status_code=201)
async def create_new_metric(metric: MetricCreate, db: Session = Depends(get_db)):
    """
    Registra uma nova métrica no sistema
    """
    try:
        return create_metric(db=db, metric=metric)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao registrar métrica: {str(e)}"
        )

@router.get("/metrics", response_model=List[MetricResponse])
async def list_metrics(
    user_id: int = None, 
    platform_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Lista métricas com filtros opcionais
    """
    return get_metrics(db=db, user_id=user_id, platform_id=platform_id)