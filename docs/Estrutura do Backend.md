# Estrutura do Backend - Social Media Metrics API

Este documento detalha a estrutura do backend para uma API RESTful desenvolvida com FastAPI, projetada para coletar métricas de redes sociais (X, Facebook, Instagram, WhatsApp, TikTok). Inclui a arquitetura do sistema, estrutura de arquivos, fluxos de usuário, esquema do banco de dados, e configurações, com base em 140 prompts otimizados para VibeCoding. O projeto usa PostgreSQL local, comandos Git via MCP Server, e autenticação via tokens (sem senhas).

## Arquitetura do Sistema

- **Componentes Principais**:
  - **API FastAPI**: Servidor HTTP que expõe endpoints para gerenciar usuários (`/users/`), plataformas (`/platforms/`), métricas (`/metrics/`), autenticação (`/auth/`, `/users/register-token/`), consentimento (`/consent/`), e webhooks.
  - **Banco de Dados PostgreSQL**: Armazena dados em três tabelas: `users`, `platforms`, `metrics`. Usa SQLAlchemy para ORM e Alembic para migrações.
  - **Celery + Redis**: Executa tarefas assíncronas (ex.: coleta diária de métricas, limpeza de dados antigos). Celery Beat agenda tarefas.
  - **Clientes HTTP**: Integração com APIs externas (X API v2, Meta Graph API, WhatsApp Business API, TikTok API) usando OAuth 2.0 ou tokens.
  - **Segurança**: Autenticação JWT, criptografia AES-256 para `access_token`, conformidade com LGPD via endpoint `/consent/`.
  - **Logging e Monitoramento**: Logs em formato JSON, rate limiting para APIs externas, cache com Redis.

- **Fluxo de Dados**:
  - Usuários registram tokens via POST `/users/register-token/`.
  - Tarefas Celery coletam métricas das APIs externas e salvam na tabela `metrics`.
  - Endpoints GET `/metrics/` permitem consultas filtradas (ex.: por usuário, plataforma, período).
  - Webhooks (WhatsApp, Instagram) atualizam métricas em tempo real.

## Estrutura de Arquivos

```
social-media-metrics-api/
├── app/
│   ├── __init__.py                   # Inicializa o módulo
│   ├── main.py                      # FastAPI com CORS, endpoint /health
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── users.py             # Endpoints /users/, /users/register-token/, /users/{user_id}/tokens/
│   │   │   ├── platforms.py         # Endpoints /platforms/
│   │   │   ├── metrics.py           # Endpoints /metrics/
│   │   │   ├── webhooks.py          # Webhooks para WhatsApp, Instagram
│   │   ├── dependencies.py          # Dependências (ex.: autenticação JWT)
│   ├── core/
│   │   ├── config.py                # Configurações (DATABASE_URL, API_KEYS)
│   │   ├── logging.py               # Logging em JSON
│   │   ├── security.py              # Criptografia AES-256, rotação de tokens
│   │   ├── auth.py                  # Autenticação JWT, /auth/login
│   │   ├── compliance.py            # LGPD, endpoint /consent/
│   │   ├── cache.py                 # Cache com Redis
│   │   ├── rate_limiter.py          # Limites de requisições
│   ├── db/
│   │   ├── database.py              # Conexão PostgreSQL com SQLAlchemy
│   │   ├── models.py                # Modelos User, Platform, Metric
│   │   ├── crud.py                  # Funções CRUD
│   ├── services/
│   │   ├── api_clients.py           # Clientes HTTP para APIs externas
│   │   ├── x_client.py              # X API v2 (impressões, retweets)
│   │   ├── meta_client.py           # Meta API (Facebook, Instagram)
│   │   ├── whatsapp_client.py       # WhatsApp Business API
│   │   ├── tiktok_client.py         # TikTok API
│   │   ├── token_manager.py         # Criptografia de access_token
│   ├── tasks.py                     # Tarefas Celery
├── tests/
│   ├── test_users.py                # Testes para /users/
│   ├── test_platforms.py            # Testes para /platforms/
│   ├── test_metrics.py              # Testes para /metrics/
│   ├── test_api_clients.py          # Testes para clientes HTTP
│   ├── test_db_failure.py           # Testes de resiliência
│   ├── load_test.py                 # Testes de carga com locust
├── scripts/
│   ├── populate_db.py               # Dados de teste
│   ├── optimize_db.py               # Otimização do banco
│   ├── backup_env.py                # Backup do .env
│   ├── restore_db.py                # Restauração de backups
├── docs/
│   ├── architecture.md              # Arquitetura do sistema
│   ├── database_schema.md           # Esquema do banco
│   ├── api_endpoints.md             # Documentação dos endpoints
│   ├── api_integration.md           # APIs externas
│   ├── scheduling.md                # Celery e Redis
│   ├── compliance.md                # LGPD e GDPR
│   ├── tests.md                     # Testes
│   ├── maintenance.md               # Manutenção
│   ├── adding_platforms.md          # Adicionar plataformas
│   ├── onboarding.md                # Tutorial para desenvolvedores
│   ├── issue_template.md            # Modelo de issues
│   ├── doc_review.md                # Revisão da documentação
│   ├── maintenance_checklist.md     # Checklist mensal
│   ├── retrospective.md             # Retrospectiva
│   ├── token_management.md          # Gestão de tokens
├── alembic/
│   ├── versions/                    # Migrações do banco
├── .env                             # Variáveis de ambiente
├── .gitignore                       # Exclui venv/, .env
├── requirements.txt                 # Dependências
├── setup.sh                         # Configura ambiente
├── run.sh                           # Inicia servidor
├── celeryconfig.py                  # Celery Beat
├── .flake8                          # Linter
├── pyproject.toml                   # Black
├── pytest.ini                       # Pytest
├── docker-compose.yml               # Redis e Celery
├── CHANGELOG.md                     # Alterações
```

## Esquema do Banco de Dados

- **Tabela `users`**:
  - `user_id` (SERIAL PRIMARY KEY)
  - `name` (VARCHAR(255))
  - `email` (VARCHAR(255) UNIQUE)
  - `platform_user_id` (VARCHAR(255))
  - `access_token` (TEXT, criptografado)
  - Constraint: UNIQUE(`platform_id`, `platform_user_id`)

- **Tabela `platforms`**:
  - `platform_id` (SERIAL PRIMARY KEY)
  - `name` (VARCHAR(50) UNIQUE, ex.: Instagram)
  - `api_key` (VARCHAR(255))

- **Tabela `metrics`**:
  - `metric_id` (SERIAL PRIMARY KEY)
  - `user_id` (INT, FK → users.user_id)
  - `platform_id` (INT, FK → platforms.platform_id)
  - `metric_type` (VARCHAR(50), ex.: impressões)
  - `value` (NUMERIC)
  - `collected_at` (TIMESTAMP)
  - Índices: `user_id`, `platform_id`, `collected_at`

## Fluxos de Usuário

### Fluxo 1: Registro de Token (Cliente)
- **Descrição**: Cliente associa `platform_user_id` e `access_token` para coleta de métricas.
- **Passos**:
  1. Login via POST `/auth/login` (JWT retornado).
  2. Requisição POST `/users/register-token/` com `platform_user_id`, `access_token`, `platform_id`.
  3. Token criptografado e armazenado.
- **Exemplo**:
  ```http
  POST /users/register-token/
  Authorization: Bearer <jwt_token>
  Content-Type: application/json
  {
    "platform_user_id": "123456789",
    "access_token": "abc123xyz",
    "platform_id": 3
  }
  Response: 201 Created
  { "message": "Token registered successfully" }
  ```

### Fluxo 2: Consulta de Métricas (Cliente)
- **Descrição**: Cliente visualiza métricas filtradas.
- **Passos**:
  1. Login via POST `/auth/login`.
  2. Requisição GET `/metrics/` com filtros (`user_id`, `platform`, `start_date`, `end_date`).
  3. Retorno de métricas em JSON.
- **Exemplo**:
  ```http
  GET /metrics/?user_id=1&platform=Instagram&start_date=2025-01-01&end_date=2025-05-01
  Authorization: Bearer <jwt_token>
  Response: 200 OK
  [
    {
      "metric_id": 1,
      "user_id": 1,
      "platform_id": 3,
      "metric_type": "impressions",
      "value": 1000,
      "collected_at": "2025-01-02T10:00:00Z"
    }
  ]
  ```

### Fluxo 3: Gerenciamento de Usuários (Administrador)
- **Descrição**: Administrador cria, atualiza, ou exclui usuários.
- **Passos**:
  1. Login com credenciais privilegiadas.
  2. Uso de endpoints POST/GET/PUT/DELETE `/users/`.
- **Exemplo** (POST `/users/`):
  ```http
  POST /users/
  Authorization: Bearer <admin_jwt_token>
  Content-Type: application/json
  {
    "name": "João Silva",
    "email": "joao@exemplo.com",
    "platform_user_id": "123456789",
    "access_token": "abc123xyz"
  }
  Response: 201 Created
  { "user_id": 1, "name": "João Silva", "email": "joao@exemplo.com" }
  ```

### Fluxo 4: Coleta Automática (Sistema)
- **Descrição**: Coleta periódica de métricas.
- **Passos**:
  1. Tarefa Celery agendada (diária) coleta métricas via clientes HTTP.
  2. Dados salvos na tabela `metrics`.
  3. Logs registrados.
- **Configuração**:
  ```python
  # app/tasks.py
  from celery import shared_task
  @shared_task
  def collect_metrics():
      # Lógica para coletar métricas de todos os usuários
      pass
  ```

### Fluxo 5: Consentimento LGPD (Cliente)
- **Descrição**: Registro de consentimento para coleta de dados.
- **Passos**:
  1. Login via POST `/auth/login`.
  2. Requisição POST `/consent/`.
- **Exemplo**:
  ```http
  POST /consent/
  Authorization: Bearer <jwt_token>
  Content-Type: application/json
  { "user_id": 1, "consent_given": true }
  Response: 201 Created
  { "message": "Consent recorded" }
  ```

## Configurações

- **Dependências** (`requirements.txt`):
  - `fastapi`, `uvicorn`, `pydantic`, `requests`, `psycopg2`, `sqlalchemy`, `cryptography`, `python-dotenv`, `celery`, `redis`, `tenacity`
- **Variáveis de Ambiente** (`.env`):
  ```env
  DATABASE_URL=postgresql://user:password@localhost:5432/social_metrics_db
  API_KEYS=your_api_keys_here
  CELERY_BROKER_URL=redis://localhost:6379/0
  ```
- **Ferramentas**:
  - Linter: `flake8` (max-line-length=88)
  - Formatador: `black`
  - Testes: `pytest` com `pytest-cov` (cobertura >80%)
  - CI: GitHub Actions (`.github/workflows/ci.yml`)
- **Segurança**:
  - HTTPS com certificados autoassinados (desenvolvimento).
  - Criptografia AES-256 para `access_token`.
  - Auditoria de acesso a dados sensíveis.