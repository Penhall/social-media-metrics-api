# Plano de Implementação para Tarefas Pendentes

## 🔴 Tarefas Prioritárias (Alta/Média)

1. **Refresh Tokens (2 dias)**
   - Criar `scripts/refresh_tokens.py`
   - Implementar scheduler no Celery
   - Adicionar tratamento de erros
   - Testar com tokens expirados

2. **Data Processor (4 dias)**
   - Unificar formatos em `app/utils/data_processor.py`:
     - Seguidores: sempre como integer
     - Taxas: sempre como float (0-1)
     - Datas: formato ISO 8601
   - Implementar transformers específicos por plataforma
   - Validar schemas usando Pydantic
   - Adicionar tratamento para dados inconsistentes

3. **Retry Mechanism (2 dias)**
   - Finalizar `app/utils/retry.py`
   - Implementar backoff exponencial
   - Adicionar circuit breaker
   - Integrar com serviços existentes

4. **Batch Processing (5 dias)**
   - Criar `app/utils/batch_processor.py`
   - Implementar filas com Redis
   - Adicionar controle de progresso
   - Testar com grandes volumes

## 🟡 Tarefas Parcialmente Concluídas

1. **Tasks Assíncronas (2 dias)**
   - Implementar sistema de prioridades (0-9) em `app/workers/tasks.py`
   - Adicionar timeouts configuráveis por task
   - Melhorar logging com correlation IDs
   - Criar filas separadas no Celery (alta, media, baixa)

2. **Tratamento de Erros (1 dia)**
   - Adicionar logs detalhados
   - Implementar notificações
   - Criar dashboard de erros

3. **Webhooks (2 dias)**
   - Implementar HMAC verification em `app/api/endpoints/webhooks.py`
   - Adicionar secret key no `.env` (WEBHOOK_SECRET)
   - Criar middleware de validação

## 📅 Cronograma Recomendado

| Semana | Tarefas |
|--------|---------|
| 1 | Refresh Tokens + Retry Mechanism |
| 2 | Data Processor + Tasks Assíncronas |
| 3 | Batch Processing + Webhooks |
| 4 | Trends Service + NLP Integration |

## 👨‍💻 Alocação de Recursos

- **Dev Sênior**: Data Processor + Batch Processing
- **Dev Pleno**: Refresh Tokens + Retry Mechanism  
- **Dev Júnior**: Tasks Assíncronas + Webhooks