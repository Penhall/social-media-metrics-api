from celery import Celery
from datetime import timedelta
from app.core.config import settings
from app.services.facebook_service import FacebookService
from scripts.refresh_tokens import TokenRefresher

app = Celery('tasks', broker=settings.CELERY_BROKER_URL)

# Configuração de agendamento
app.conf.beat_schedule = {
    'refresh-tokens-daily': {
        'task': 'app.workers.tasks.refresh_tokens',
        'schedule': timedelta(days=1),
        'options': {'queue': 'maintenance'}
    },
}

@app.task(bind=True, max_retries=3)
def refresh_tokens(self):
    """Tarefa agendada para refresh de tokens OAuth2"""
    try:
        refresher = TokenRefresher()
        refresher.refresh_all_tokens()
    except Exception as e:
        self.retry(exc=e, countdown=300)

@app.task
def process_facebook_event(event_type: str, event_data: dict, page_id: str):
    """Processa eventos do Facebook de forma assíncrona"""
    fb_service = FacebookService()
    
    try:
        if event_type == "feed":
            # Processar novos posts/comentários
            fb_service.process_feed_event(event_data, page_id)
        elif event_type == "mention":
            # Processar menções
            fb_service.process_mention(event_data, page_id)
        elif event_type == "messages":
            # Processar mensagens
            fb_service.process_message(event_data, page_id)
            
    except Exception as e:
        # TODO: Implementar retry e logging
        raise self.retry(exc=e, countdown=60)