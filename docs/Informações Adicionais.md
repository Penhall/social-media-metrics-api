# Informações Adicionais - Social Media Metrics API

Este documento fornece informações complementares para o desenvolvimento da API de coleta de métricas de redes sociais, incluindo uma proposta de interface frontend, wireframes textuais, e contexto para maximizar o uso das ferramentas RooCode, Cline, e Cursor. O foco é fornecer detalhes para a implementação, especialmente para a integração com uma UI e orientações para as ferramentas.

## Proposta de Interface Frontend

Embora os prompts foquem no backend, propomos uma **dashboard web** com React e Material-UI para consumir a API FastAPI, permitindo visualizar métricas, gerenciar usuários, e registrar tokens.

### Funcionalidades
- **Login**: Autenticação via POST `/auth/login`.
- **Dashboard de Métricas**: Gráficos e tabelas para métricas (GET `/metrics/`).
- **Gerenciamento de Usuários**: Tabela para CRUD de usuários (POST/GET/PUT/DELETE `/users/`).
- **Registro de Tokens**: Formulário para POST `/users/register-token/`.
- **Consentimento LGPD**: Formulário para POST `/consent/`.

### Páginas
1. **Login**:
   - Campos: Email, senha.
   - Botão: "Entrar".
2. **Dashboard**:
   - Filtros: Usuário, plataforma, período.
   - Gráficos: Linha (métricas ao longo do tempo), barras (por plataforma).
   - Tabela: Métricas recentes.
3. **Gerenciamento de Usuários** (admin):
   - Tabela: ID, nome, email, plataformas.
   - Botões: Adicionar, editar, excluir.
4. **Registro de Tokens**:
   - Formulário: Plataforma, `platform_user_id`, `access_token`.
5. **Consentimento LGPD**:
   - Checkbox: "Concordo com a coleta de dados".
   - Botão: "Enviar".

### Wireframe Textual (Dashboard)
```
----------------------------------------
| Social Media Metrics Dashboard       |
----------------------------------------
| [Logout]                             |
----------------------------------------
| Filtros:                             |
| Usuário: [Dropdown]                  |
| Plataforma: [Dropdown: X, Instagram] |
| Período: [Data Inicial] [Data Final] |
| [Filtrar]                            |
----------------------------------------
| Gráfico de Linha: Impressões         |
| [Gráfico com eixos X=tempo, Y=valor] |
----------------------------------------
| Tabela de Métricas                   |
| ID | Plataforma | Tipo | Valor | Data |
| 1  | Instagram  | Impressões | 1000 | 2025-01-02 |
| 2  | X          | Retweets   | 50   | 2025-01-03 |
----------------------------------------
```

### Estilo Visual
- **Cores**: Azul (#1976D2) para botões, cinza claro (#F5F5F5) para fundo.
- **Tipografia**: Roboto (Material-UI).
- **Componentes**:
  - Botões arredondados.
  - Tabelas com alternância de cores.
  - Gráficos interativos (Chart.js).
- **Responsividade**: Layout adaptável (Material-UI Grid).

### Exemplo de Código (React)
```jsx
// src/components/Dashboard.js
import React, { useState, useEffect } from "react";
import { Container, TextField, Button, Select, MenuItem } from "@mui/material";
import { Line } from "react-chartjs-2";
import axios from "axios";

const Dashboard = () => {
  const [filters, setFilters] = useState({
    userId: "",
    platform: "",
    startDate: "",
    endDate: "",
  });
  const [metrics, setMetrics] = useState([]);

  const fetchMetrics = async () => {
    try {
      const response = await axios.get("http://localhost:8000/metrics/", {
        headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        params: filters,
      });
      setMetrics(response.data);
    } catch (error) {
      console.error("Error fetching metrics:", error);
    }
  };

  return (
    <Container>
      <h1>Social Media Metrics</h1>
      <div>
        <Select
          value={filters.platform}
          onChange={(e) => setFilters({ ...filters, platform: e.target.value })}
        >
          <MenuItem value="Instagram">Instagram</MenuItem>
          <MenuItem value="X">X</MenuItem>
        </Select>
        <TextField
          label="Data Inicial"
          type="date"
          value={filters.startDate}
          onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
        />
        <TextField
          label="Data Final"
          type="date"
          value={filters.endDate}
          onChange={(e) => setFilters({ ...filters, endDate: e.target.value })}
        />
        <Button onClick={fetchMetrics}>Filtrar</Button>
      </div>
      <Line
        data={{
          labels: metrics.map((m) => m.collected_at),
          datasets: [
            {
              label: "Impressões",
              data: metrics.map((m) => m.value),
              borderColor: "#1976D2",
            },
          ],
        }}
      />
    </Container>
  );
};

export default Dashboard;
```

## Contexto para Ferramentas

### Uso dos Prompts
Os 420 prompts (140 por ferramenta: RooCode, Cline, Cursor) estão divididos em 9 categorias:
- Configuração Inicial (1-15)
- Banco de Dados (16-30)
- Backend FastAPI (31-50)
- Integração com APIs (51-80)
- Agendamento e Escalabilidade (81-95)
- Segurança e Conformidade (96-110)
- Testes e Qualidade (111-125)
- Documentação e Manutenção (141-150)
- Autenticação de Usuários (151-155)

**Recomendações**:
- **Ordem de Implementação**: Comece com Configuração Inicial, seguida por Banco de Dados e Backend FastAPI.
- **Testes Iniciais**:
  - Tarefa 1: Criar repositório GitHub.
  - Tarefa 12: Executar `run.sh` para iniciar o servidor.
  - Tarefa 16: Criar banco `social_metrics_db` com `psql`.
- **Ferramentas**:
  - **RooCode**: Use modos Architect (planejamento), Code (geração), Ask (dúvidas), QA (testes).
  - **Cline**: Use Plan Mode para planejamento e Act Mode para execução com aprovação manual.
  - **Cursor**: Use Cursor Composer para código, Cursor Ask para dúvidas, Agent para automação.

### Configurações Recomendadas
- **Ambiente**:
  - Python 3.8+ com `venv`.
  - PostgreSQL instalado localmente (`social_metrics_db`).
  - Redis para Celery (`docker-compose.yml`).
  - MCP Server para comandos Git (`gh` CLI).
- **Ferramentas de Desenvolvimento**:
  - VS Code com extensões RooCode, Cline, Cursor.
  - Postman ou `curl` para testar endpoints.
  - `flake8` e `black` para linting e formatação.
- **Chaves de API**:
  - Configure chaves de teste para X API Basic, Meta Graph API, WhatsApp Business API, TikTok API.
  - Armazene em `.env` e criptografe `access_token`.

### Integração Frontend-Backend
- **CORS**: Configurado para `http://localhost` (Tarefa 31).
- **Autenticação**: Frontend envia JWT em todas as requisições.
- **Requisições**:
  - GET `/metrics/` para gráficos.
  - POST `/users/register-token/` para formulário de tokens.
  - POST `/consent/` para LGPD.
- **Erro Handling**: Exibir mensagens para erros 400, 401, 404.

## Orientações para Implementação
- **Kanban**:
  - Crie um quadro Trello/Jira com colunas: To Do, In Progress, Review, Done.
  - Adicione prompts como tarefas, agrupados por categoria.
  - Exemplo:
    ```markdown
    **Tarefa 1: Criar Repositório**
    - Prompt: "Use o Agent para criar um repositório Git no GitHub..."
    - Categoria: Configuração Inicial
    - Estimativa: 1 hora
    ```
- **Repositório GitHub**:
  - Estruture prompts em `/prompts/roocode/`, `/prompts/cline/`, `/prompts/cursor/`.
  - Exemplo:
    ```
    /prompts/
      /cursor/
        config.md
        database.md
      /roocode/
      /cline/
    README.md
    ```
- **Testes**:
  - Valide endpoints com Postman (ex.: GET `/health`).
  - Execute `pytest` para cobertura >80%.
  - Teste webhooks com ngrok para URLs públicas.