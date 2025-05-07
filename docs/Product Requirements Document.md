# Product Requirements Document - Social Media Metrics API

## 1. Visão Geral

### 1.1 Objetivo
Desenvolver uma **API RESTful** com FastAPI para coletar, armazenar, e consultar métricas de redes sociais (X, Facebook, Instagram, WhatsApp, TikTok), integrada a uma **dashboard web** (React) para visualização. A API suporta autenticação via tokens, conformidade com LGPD, e coleta automática de métricas, atendendo marcas, influenciadores, e agências de marketing.

### 1.2 Público-Alvo
- **Clientes**: Marcas, influenciadores, e agências que monitoram engajamento em redes sociais.
- **Administradores**: Equipes internas que gerenciam usuários e plataformas.
- **Desenvolvedores**: Equipes técnicas que integram ou estendem a API.

### 1.3 Proposta de Valor
- **Centralização**: Consolida métricas de múltiplas plataformas em um único sistema.
- **Automatização**: Coleta periódica de métricas via tarefas agendadas.
- **Segurança**: Autenticação JWT, criptografia de tokens, e conformidade com LGPD.
- **Usabilidade**: Dashboard intuitiva para visualização de métricas.

## 2. Funcionalidades

### 2.1 Backend (API)
- **Gerenciamento de Usuários**:
  - CRUD de usuários (POST/GET/PUT/DELETE `/users/`).
  - Registro de tokens por plataforma (POST `/users/register-token/`).
  - Listagem de plataformas associadas (GET `/users/{user_id}/tokens/`).
- **Gerenciamento de Plataformas**:
  - Cadastro de plataformas (POST `/platforms/`).
  - Listagem de plataformas (GET `/platforms/`).
- **Coleta de Métricas**:
  - Registro manual de métricas (POST `/metrics/`).
  - Consulta com filtros (GET `/metrics/?user_id=&platform=&start_date=&end_date=`).
  - Coleta automática diária via Celery.
- **Integração com APIs Externas**:
  - Suporte a X API v2, Meta Graph API, WhatsApp Business API, TikTok API.
  - Webhooks para atualizações em tempo real (WhatsApp, Instagram).
- **Autenticação e Segurança**:
  - Login com JWT (POST `/auth/login`).
  - Criptografia AES-256 para `access_token`.
  - Consentimento LGPD (POST `/consent/`).
- **Health Check**:
  - Endpoint GET `/health` para verificar status da API.

### 2.2 Frontend (Dashboard Web)
- **Login**:
  - Formulário para email e senha, integrado com POST `/auth/login`.
- **Dashboard de Métricas**:
  - Filtros: Usuário, plataforma, período.
  - Gráficos: Linha (métricas ao longo do tempo), barras (comparação por plataforma).
  - Tabela: Lista de métricas recentes.
- **Gerenciamento de Usuários** (admin):
  - Tabela com CRUD de usuários.
- **Registro de Tokens**:
  - Formulário para plataforma, `platform_user_id`, `access_token`.
- **Consentimento LGPD**:
  - Formulário com checkbox para consentimento.

## 3. Fluxos de Usuário

### 3.1 Registro de Token (Cliente)
- **Descrição**: Cliente associa `platform_user_id` e `access_token` para coleta.
- **Passos**:
  1. Login via POST `/auth/login` (JWT retornado).
  2. Acessa formulário na dashboard.
  3. Envia POST `/users/register-token/` com `platform_user_id`, `access_token`, `platform_id`.
  4. Recebe confirmação.
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

### 3.2 Consulta de Métricas (Cliente)
- **Descrição**: Cliente visualiza métricas filtradas na dashboard.
- **Passos**:
  1. Login via POST `/auth/login`.
  2. Seleciona filtros na dashboard (usuário, plataforma, período).
  3. Dashboard envia GET `/metrics/` e exibe gráficos/tabela.
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

### 3.3 Gerenciamento de Usuários (Administrador)
- **Descrição**: Administrador gerencia usuários via dashboard.
- **Passos**:
  1. Login com credenciais privilegiadas.
  2. Acessa tabela de usuários na dashboard.
  3. Executa ações (criar, editar, excluir) via POST/GET/PUT/DELETE `/users/`.
- **Exemplo**:
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

### 3.4 Coleta Automática (Sistema)
- **Descrição**: Sistema coleta métricas diariamente.
- **Passos**:
  1. Tarefa Celery agendada (via Celery Beat) executa coleta para todos os usuários.
  2. Clientes HTTP acessam APIs externas e salvam dados em `metrics`.
  3. Logs registrados.

### 3.5 Consentimento LGPD (Cliente)
- **Descrição**: Cliente registra consentimento na dashboard.
- **Passos**:
  1. Login via POST `/auth/login`.
  2. Marca checkbox na dashboard e envia POST `/consent/`.
- **Exemplo**:
  ```http
  POST /consent/
  Authorization: Bearer <jwt_token>
  Content-Type: application/json
  { "user_id": 1, "consent_given": true }
  Response: 201 Created
  { "message": "Consent recorded" }
  ```

## 4. Requisitos

### 4.1 Funcionais
- **API**:
  - Suportar CRUD de usuários, plataformas, e métricas.
  - Integrar com 5 APIs externas (X, Meta, WhatsApp, TikTok).
  - Coletar métricas automaticamente a cada 24 horas.
  - Suportar webhooks para WhatsApp e Instagram.
  - Implementar autenticação JWT e criptografia AES-256.
  - Registrar consentimento LGPD.
- **Frontend**:
  - Exibir dashboard com filtros e gráficos.
  - Permitir gerenciamento de usuários (admin).
  - Suportar registro de tokens e consentimento.

### 4.2 Não Funcionais
- **Desempenho**: Coleta de métricas em <5 segundos por usuário.
- **Escalabilidade**: Suportar 100 usuários simultâneos (testes de carga).
- **Segurança**:
  - HTTPS com certificados autoassinados (desenvolvimento).
  - Auditoria de acesso a dados sensíveis.
- **Testes**: Cobertura de testes >80% (pytest-cov).
- **Conformidade**: LGPD e GDPR (registro de consentimento).
- **Manutenibilidade**: Documentação completa (endpoints, arquitetura, testes).

## 5. Arquitetura do Sistema

### 5.1 Componentes
- **API FastAPI**: Servidor HTTP com endpoints RESTful.
- **PostgreSQL**: Banco com tabelas `users`, `platforms`, `metrics`.
- **Celery + Redis**: Tarefas assíncronas e agendamento.
- **Clientes HTTP**: Integração com APIs externas via OAuth 2.0/tokens.
- **Frontend**: React com Material-UI, consumindo API via HTTP.
- **Segurança**: JWT, criptografia AES-256, conformidade LGPD.

### 5.2 Esquema do Banco de Dados
- **Tabela `users`**:
  - `user_id` (SERIAL PRIMARY KEY)
  - `name` (VARCHAR(255))
  - `email` (VARCHAR(255) UNIQUE)
  - `platform_user_id` (VARCHAR(255))
  - `access_token` (TEXT, criptografado)
  - Constraint: UNIQUE(`platform_id`, `platform_user_id`)
- **Tabela `platforms`**:
  - `platform_id` (SERIAL PRIMARY KEY)
  - `name` (VARCHAR(50) UNIQUE)
  - `api_key` (VARCHAR(255))
- **Tabela `metrics`**:
  - `metric_id` (SERIAL PRIMARY KEY)
  - `user_id` (INT, FK → users.user_id)
  - `platform_id` (INT, FK → platforms.platform_id)
  - `metric_type` (VARCHAR(50))
  - `value` (NUMERIC)
  - `collected_at` (TIMESTAMP)
  - Índices: `user_id`, `platform_id`, `collected_at`

### 5.3 Estrutura de Arquivos (Backend)
```
social-media-metrics-api/
├── app/
│   ├── main.py                      # FastAPI, CORS, /health
│   ├── api/endpoints/
│   │   ├── users.py                # /users/, /users/register-token/
│   │   ├── platforms.py            # /platforms/
│   │   ├── metrics.py              # /metrics/
│   │   ├── webhooks.py             # Webhooks
│   ├── core/
│   │   ├── config.py               # Configurações
│   │   ├── logging.py              # Logging JSON
│   │   ├── security.py             # Criptografia
│   │   ├── auth.py                 # JWT, /auth/login
│   │   ├── compliance.py           # LGPD, /consent/
│   ├── db/
│   │   ├── database.py             # Conexão PostgreSQL
│   │   ├── models.py               # Modelos SQLAlchemy
│   │   ├── crud.py                 # CRUD
│   ├── services/
│   │   ├── api_clients.py          # Clientes HTTP
│   │   ├── x_client.py             # X API
│   │   ├── meta_client.py          # Meta API
│   │   ├── whatsapp_client.py      # WhatsApp API
│   │   ├── tiktok_client.py        # TikTok API
│   ├── tasks.py                    # Tarefas Celery
├── tests/                          # Testes pytest
├── scripts/                        # Scripts utilitários
├── docs/                           # Documentação
├── alembic/                        # Migrações
├── .env, requirements.txt, etc.
```

### 5.4 Estrutura de Arquivos (Frontend)
```
frontend/
├── src/
│   ├── components/
│   │   ├── Login.js               # Página de login
│   │   ├── Dashboard.js           # Dashboard de métricas
│   │   ├── UserManagement.js      # Gerenciamento de usuários
│   │   ├── TokenRegistration.js   # Registro de tokens
│   │   ├── ConsentForm.js         # Consentimento LGPD
│   ├── App.js                     # Rotas e layout
├── package.json                   # Dependências (React, Material-UI, Chart.js)
```

## 6. Critérios de Sucesso
- **Funcionais**:
  - API suporta todas as operações CRUD e integração com 5 plataformas.
  - Dashboard exibe métricas com filtros e gráficos.
  - Consentimento LGPD registrado para todos os usuários.
- **Não Funcionais**:
  - Tempo de coleta <5 segundos por usuário.
  - Cobertura de testes >80%.
  - Zero vulnerabilidades críticas (relatório `bandit`).
- **Usabilidade**:
  - Dashboard responsiva (desktop e mobile).
  - Tempo de aprendizado <10 minutos para novos usuários.

## 7. Premissas e Dependências
- **Premissas**:
  - APIs externas fornecem acesso a métricas via OAuth 2.0/tokens.
  - Usuários fornecem `access_token` válidos.
  - Ambiente local com Python 3.8+, PostgreSQL, Redis.
- **Dependências**:
  - Backend: `fastapi`, `sqlalchemy`, `celery`, `redis`, `cryptography`.
  - Frontend: `react`, `material-ui`, `chart.js`, `axios`.
  - Ferramentas: RooCode, Cline, Cursor, MCP Server (`gh` CLI).

## 8. Riscos e Mitigações
- **Risco**: Limites de requisições das APIs externas.
  - **Mitigação**: Implementar rate limiting e cache (Redis).
- **Risco**: Falhas nas APIs externas.
  - **Mitigação**: Mecanismo de retry com `tenacity`.
- **Risco**: Problemas de segurança (ex.: vazamento de tokens).
  - **Mitigação**: Criptografia AES-256, auditoria de acesso.

## 9. Cronograma Estimado
- **Fase 1: Configuração e Banco (2 semanas)**:
  - Tarefas 1-30 (Configuração Inicial, Banco de Dados).
- **Fase 2: Backend e Integração (4 semanas)**:
  - Tarefas 31-80 (Backend FastAPI, Integração com APIs).
- **Fase 3: Agendamento e Segurança (2 semanas)**:
  - Tarefas 81-110 (Agendamento, Segurança).
- **Fase 4: Testes e Documentação (2 semanas)**:
  - Tarefas 111-125, 141-150 (Testes, Documentação).
- **Fase 5: Autenticação e Frontend (2 semanas)**:
  - Tarefas 151-155 (Autenticação).
  - Desenvolvimento da dashboard React.
- **Total**: ~12 semanas.