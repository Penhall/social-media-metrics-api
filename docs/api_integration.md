# Documentação de Integração da API

## Visão Geral
A API fornece endpoints para:
- Gerenciamento de métricas de redes sociais
- Gerenciamento de usuários
- Recebimento de webhooks

**URL Base**: `https://api.example.com/api/v1`

## Autenticação
```http
Authorization: Bearer {token}
X-API-Key: {chave_api}
```

## Endpoints

### Métricas

#### `POST /metrics`
Registra uma nova métrica no sistema

**Request**:
```json
{
  "name": "engajamento",
  "value": 42.5,
  "user_id": 1,
  "platform_id": 2
}
```

**Response** (201 Created):
```json
{
  "id": 123,
  "name": "engajamento",
  "value": 42.5,
  "created_at": "2025-05-14T12:00:00Z"
}
```

#### `GET /metrics`
Lista métricas com filtros opcionais

**Parâmetros Query**:
- `user_id`: Filtra por usuário
- `platform_id`: Filtra por plataforma

**Response** (200 OK):
```json
[
  {
    "id": 123,
    "name": "engajamento",
    "value": 42.5,
    "created_at": "2025-05-14T12:00:00Z"
  }
]
```

#### `GET /metrics/twitter/{username}`
Obtém métricas de um usuário do Twitter

**Response** (200 OK):
```json
{
  "username": "exemplo",
  "followers": 1500,
  "engagement_rate": 3.2
}
```

#### `GET /metrics/twitter/tweets/{tweet_id}`
Obtém métricas de um tweet específico

**Response** (200 OK):
```json
{
  "tweet_id": "12345",
  "likes": 42,
  "retweets": 5,
  "replies": 3
}
```

### Usuários

#### `POST /users`
Cria um novo usuário no sistema

**Request**:
```json
{
  "name": "João Silva",
  "email": "joao@example.com"
}
```

**Response** (201 Created):
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com"
}
```

#### `GET /users/{user_id}`
Busca um usuário pelo ID

**Response** (200 OK):
```json
{
  "id": 1,
  "name": "João Silva",
  "email": "joao@example.com"
}
```

### Webhooks

#### `POST /{platform}`
Recebe webhooks de plataformas sociais

**Headers obrigatórios**:
```
X-Signature: {assinatura_hmac}
X-Signature-Algo: sha256
```

**Request**:
```json
{
  "event": "message",
  "data": {...}
}
```

**Response** (200 OK):
```json
{
  "status": "received",
  "platform": "facebook"
}
```

## Limitações e Quotas
- 100 requisições/minuto por API Key
- Webhooks: 5 eventos/segundo por plataforma

## Instruções para Desenvolvedores
1. Configure suas credenciais no `.env`
2. Para webhooks, implemente validação HMAC
3. Considere usar cache para métricas frequentes
4. Trate erros com códigos HTTP apropriados