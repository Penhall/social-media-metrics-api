from celery import shared_task
from typing import Dict, List
import logging
from datetime import datetime

from app.utils.api_utils import make_api_request
from app.utils.date_utils import get_date_range
from app.services.metric_service import create_metric
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

@shared_task(bind=True, name='fetch_social_metrics')
def fetch_social_metrics(self, platform: str, user_id: int) -> Dict:
    """Task para coletar métricas de redes sociais"""
    try:
        db = SessionLocal()
        
        # Implementações específicas por plataforma
        if platform == 'instagram':
            metrics = _fetch_instagram_metrics(user_id)
        elif platform == 'twitter':
            metrics = _fetch_twitter_metrics(user_id)
        else:
            raise ValueError(f"Plataforma não suportada: {platform}")

        # Salva métricas no banco
        for metric in metrics:
            create_metric(db, metric)

        return {'status': 'success', 'metrics_count': len(metrics)}
        
    except Exception as e:
        logger.error(f"Error fetching {platform} metrics: {str(e)}")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()

def _fetch_instagram_metrics(user_id: int) -> List[Dict]:
    """Implementação específica para Instagram"""
    # TODO: Implementar chamada real à API do Instagram
    start_date, end_date = get_date_range(days=7)
    return [{
        'user_id': user_id,
        'platform_id': 1,  # ID do Instagram
        'metric_name': 'followers',
        'value': 1000,
        'collected_at': datetime.now()
    }]

def _fetch_twitter_metrics(user_id: int) -> List[Dict]:
    """Implementação específica para Twitter"""
    # TODO: Implementar chamada real à API do Twitter
    start_date, end_date = get_date_range(days=7)
    return [{
        'user_id': user_id,
        'platform_id': 2,  # ID do Twitter
        'metric_name': 'followers',
        'value': 500,
        'collected_at': datetime.now()
    }]