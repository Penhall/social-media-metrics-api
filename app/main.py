from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.utils.correlation import CorrelationIdMiddleware

app = FastAPI()

# Middleware para Correlation IDs
app.add_middleware(CorrelationIdMiddleware)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    # Inicializar conexões com banco de dados e Redis aqui
    pass