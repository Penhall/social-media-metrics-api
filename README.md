# Social Media Metrics API

API para coleta e análise de métricas de redes sociais (Twitter, Facebook, Instagram, TikTok, WhatsApp)

## Visão Geral
- Coleta automatizada de métricas via APIs oficiais
- Armazenamento em banco PostgreSQL
- Processamento assíncrono com Celery
- Dashboard via FastAPI/Swagger UI

## Documentação
- [Plano de Projeto](docs/1.%20Plano%20de%20Projeto%20para%20Aplica%C3%A7%C3%A3o%20de%20Coleta%20de%20M%C3%A9tricas%20de%20Redes%20Sociais.md)
- [Diagramas UML](docs/UML%20de%20Fluxo%20e%20ER%20de%20Banco.md)
- [Wireframes](docs/Wireframes%20e%20Documenta%C3%A7%C3%A3o%20Swagger.md)

## Instalação
```bash
# Clonar repositório
git clone https://github.com/seu-usuario/social-media-metrics-api.git

# Configurar ambiente
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

## Configuração

### TikTok API
1. Obter credenciais de desenvolvedor em [TikTok for Developers](https://developers.tiktok.com/)
2. Configurar no arquivo `.env`:
```
TIKTOK_CLIENT_KEY=your_client_key
TIKTOK_CLIENT_SECRET=your_client_secret
TIKTOK_ACCESS_TOKEN=initial_access_token
TIKTOK_REFRESH_TOKEN=initial_refresh_token
```

### Redis Cache
1. Instalar Redis localmente ou configurar URL remota
2. Definir no `.env`:
```
REDIS_URL=redis://localhost:6379
```

## Execução
```bash
# Iniciar servidor FastAPI
uvicorn app.main:app --reload

# Iniciar worker Celery
celery -A app.workers.celery_worker worker --loglevel=info
```

## Estrutura do Projeto
```
├── app/               # Código fonte principal
├── tests/             # Testes automatizados
├── docs/              # Documentação técnica
├── prompts/           # Roteiros de implementação
└── scripts/           # Scripts auxiliares
```

## Roadmap
Ver [Prompts de Implementação](prompts/roocode/) para o plano detalhado de desenvolvimento