# Procedimentos de Teste End-to-End

## Configuração do Ambiente

1. Criar banco de dados de teste:
```bash
python scripts/db/create_database.py --test
```

2. Popular dados iniciais:
```bash
python scripts/db/populate_db.py --test
```

## Execução dos Testes

```bash
pytest tests/e2e/ -v
```

## Fluxos Testados

### 1. Fluxo Completo de Métricas
- Autenticação do usuário
- Obtenção de métricas consolidadas
- Persistência no banco de dados
- Histórico de consultas

### 2. Persistência no Banco
- Criação de métricas
- Verificação de persistência
- Consulta de métricas por plataforma

## Dados de Teste

Usuário padrão para testes:
- Username: `test`
- Password: `test`

Plataformas disponíveis:
- Facebook
- Instagram
- Twitter
- WhatsApp

## Troubleshooting

### Erros de Autenticação
- Verificar se o banco de testes foi populado
- Checar variáveis de ambiente no `.env.test`

### Falhas na Persistência
- Verificar conexão com o banco de testes
- Checar migrations aplicadas