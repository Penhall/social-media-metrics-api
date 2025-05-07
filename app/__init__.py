# Initialize app package
from fastapi import FastAPI

app = FastAPI(
    title="Social Media Metrics API",
    description="API para coleta e análise de métricas de redes sociais",
    version="0.1.0"
)

# Import routes
from app.api import endpoints