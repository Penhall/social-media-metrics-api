# UML de Fluxo e ER de Banco - Social Media Metrics API

Este documento fornece diagramas visuais para a **Social Media Metrics API**: um diagrama UML de sequência para o fluxo de **Registro de Token** e um diagrama ER para o banco de dados PostgreSQL. Os diagramas complementam os 420 prompts e o PRD, sem alterar o escopo.

## 1. UML de Fluxo: Diagrama de Sequência (Registro de Token)

O diagrama abaixo representa o fluxo de usuário **Registro de Token** (Fluxo 1 do PRD), onde um cliente associa um `platform_user_id` e `access_token` a uma plataforma.

```mermaid
sequenceDiagram
    participant C as Cliente
    participant F as Frontend (React)
    participant A as API (FastAPI)
    participant DB as Banco (PostgreSQL)

    C->>F: Acessa página de registro de token
    F->>C: Exibe formulário (plataforma, platform_user_id, access_token)
    C->>F: Preenche e envia formulário
    F->>A: POST /auth/login (email, senha)
    A->>DB: Valida credenciais
    DB->>A: Retorna usuário
    A->>F: Retorna JWT
    F->>A: POST /users/register-token/ (platform_user_id, access_token, platform_id, Authorization: Bearer JWT)
    A->>DB: Criptografa access_token (AES-256)
    A->>DB: Insere/Atualiza registro na tabela users
    DB->>A: Confirmação
    A->>F: 201 Created { "message": "Token registered successfully" }
    F->>C: Exibe mensagem de sucesso
```

**Notas**:
- O cliente já deve ter um `access_token` válido da plataforma (ex.: Instagram).
- A API valida o JWT antes de processar a requisição.
- O `access_token` é criptografado antes de ser salvo (Tarefa 152).

## 2. ER de Banco: Diagrama Entidade-Relacionamento

O diagrama abaixo representa o esquema do banco de dados PostgreSQL, com as tabelas `users`, `platforms`, e `metrics`, incluindo atributos, chaves primárias, estrangeiras, e índices.

```mermaid
erDiagram
    USERS ||--o{ METRICS : "tem"
    PLATFORMS ||--o{ METRICS : "tem"
    USERS {
        int user_id PK
        varchar(255) name
        varchar(255) email UK
        varchar(255) platform_user_id
        text access_token
    }
    PLATFORMS {
        int platform_id PK
        varchar(50) name UK
        varchar(255) api_key
    }
    METRICS {
        int metric_id PK
        int user_id FK
        int platform_id FK
        varchar(50) metric_type
        numeric value
        timestamp collected_at
    }
    %% Índices
    METRICS ||--o{ INDEX_USER_ID : "indexado por"
    METRICS ||--o{ INDEX_PLATFORM_ID : "indexado por"
    METRICS ||--o{ INDEX_COLLECTED_AT : "indexado por"
    %% Constraint
    USERS ||--o{ CONSTRAINT_UNIQUE : "platform_id, platform_user_id"
```

**Notas**:
- **Tabela `users`**:
  - `user_id`: Chave primária.
  - `email`: Único.
  - `access_token`: Criptografado (AES-256).
  - Constraint: Unicidade em `(platform_id, platform_user_id)` (Tarefa 29).
- **Tabela `platforms`**:
  - `platform_id`: Chave primária.
  - `name`: Único (ex.: Instagram).
- **Tabela `metrics`**:
  - `metric_id`: Chave primária.
  - `user_id` e `platform_id`: Chaves estrangeiras.
  - Índices em `user_id`, `platform_id`, `collected_at` para consultas rápidas (Tarefa 23).
- **Relacionamentos**:
  - Um usuário tem várias métricas (1:N).
  - Uma plataforma tem várias métricas (1:N).