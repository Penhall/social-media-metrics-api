from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.models import Metric
from app.schemas.metric import MetricCreate, MetricResponse
from app.schemas.social import TwitterUserMetrics, TwitterPostMetrics
from app.services.metric_service import create_metric, get_metrics
from app.services.twitter_service import TwitterService

router = APIRouter(prefix="/api/v1", tags=["metrics"])
twitter_service = TwitterService()

# Rotas para métricas internas
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
    user_id: Optional[int] = None,
    platform_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Lista métricas com filtros opcionais
    """
    return get_metrics(db=db, user_id=user_id, platform_id=platform_id)

# Rotas para integração com APIs sociais
@router.get("/metrics/twitter/{username}", response_model=TwitterUserMetrics)
async def get_twitter_user_metrics(username: str):
    """
    Obtém métricas de um usuário do Twitter
    
    Args:
        username: Nome de usuário no Twitter (sem o @)
    
    Returns:
        TwitterUserMetrics: Métricas formatadas do usuário
    """
    try:
        raw_metrics = await twitter_service.get_user_metrics(username)
        return TwitterUserMetrics(**raw_metrics["data"])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao obter métricas do Twitter: {str(e)}"
        )

@router.get("/metrics/twitter/tweets/{tweet_id}", response_model=TwitterPostMetrics)
async def get_twitter_tweet_metrics(tweet_id: str):
    """
    Obtém métricas de um tweet específico
    
    Args:
        tweet_id: ID do tweet no Twitter
    
    Returns:
        TwitterPostMetrics: Métricas formatadas do tweet
    """
    try:
        raw_metrics = await twitter_service.get_tweet_metrics(tweet_id)
        return TwitterPostMetrics(**raw_metrics["data"])
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao obter métricas do tweet: {str(e)}"
        )