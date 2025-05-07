# Wireframes e Documentação Swagger - Social Media Metrics API

Este documento fornece **wireframes textuais** para a dashboard web proposta (React) e orientações para usar o **Swagger UI** para documentar a API. Os wireframes detalham as páginas do frontend (Login, Dashboard, Gerenciamento de Usuários, Registro de Tokens, Consentimento LGPD). A seção de Swagger explica como acessar a documentação automática da API, conforme Tarefa 48 dos prompts.

## 1. Wireframes Textuais

Os wireframes abaixo representam as páginas do frontend proposto, com layout, componentes, e interações. Eles são baseados na seção 2.2 do PRD e no artefato de Informações Adicionais.

### 1.1 Página de Login
```
----------------------------------------
| Social Media Metrics - Login         |
----------------------------------------
|                                      |
| Email: [_________________________]   |
| Senha: [_________________________]   |
| [Entrar]                             |
|                                      |
----------------------------------------
```
- **Componentes**:
  - Campo de texto: Email.
  - Campo de senha: Senha.
  - Botão: "Entrar" (envia POST `/auth/login`).
- **Interações**:
  - Clique em "Entrar" valida credenciais e redireciona para a dashboard.
  - Exibe erro se credenciais inválidas (ex.: "Email ou senha incorretos").
- **Estilo**:
  - Fundo: Cinza claro (#F5F5F5).
  - Botão: Azul (#1976D2), arredondado.
  - Tipografia: Roboto.

### 1.2 Dashboard de Métricas
```
----------------------------------------
| Social Media Metrics - Dashboard     |
----------------------------------------
| [Logout]                             |
----------------------------------------
| Filtros:                             |
| Usuário: [Dropdown: João, Maria]     |
| Plataforma: [Dropdown: X, Instagram] |
| Período: [Data Inicial] [Data Final] |
| [Filtrar]                            |
----------------------------------------
| Gráfico de Linha: Impressões         |
| [Gráfico: X=tempo, Y=valor]          |
----------------------------------------
| Gráfico de Barras: Por Plataforma    |
| [Barras: X, Instagram, Facebook]     |
----------------------------------------
| Tabela de Métricas                   |
| ID | Plataforma | Tipo | Valor | Data |
| 1  | Instagram  | Impressões | 1000 | 2025-01-02 |
| 2  | X          | Retweets   | 50   | 2025-01-03 |
----------------------------------------
```
- **Componentes**:
  - Dropdown: Seleção de usuário.
  - Dropdown: Seleção de plataforma.
  - Campos de data: Período.
  - Botão: "Filtrar" (envia GET `/metrics/`).
  - Gráfico de linha: Métricas ao longo do tempo (Chart.js).
  - Gráfico de barras: Comparação por plataforma.
  - Tabela: Lista de métricas (Material-UI DataGrid).
- **Interações**:
  - Seleção de filtros atualiza gráficos e tabela.
  - Clique em "Logout" limpa JWT e redireciona para login.
- **Estilo**:
  - Gráficos: Cores contrastantes (azul, verde, roxo).
  - Tabela: Linhas alternadas (branco/cinza).

### 1.3 Gerenciamento de Usuários (Admin)
```
----------------------------------------
| Social Media Metrics - Usuários      |
----------------------------------------
| [Logout]                             |
----------------------------------------
| [Adicionar Usuário]                  |
----------------------------------------
| Tabela de Usuários                   |
| ID | Nome | Email | Plataformas     |
| 1  | João | joao@exemplo.com | X, Instagram |
| 2  | Maria | maria@exemplo.com | Facebook |
| [Editar] [Excluir]                   |
----------------------------------------
```
- **Componentes**:
  - Botão: "Adicionar Usuário" (abre formulário).
  - Tabela: Lista de usuários (GET `/users/`).
  - Botões por linha: "Editar" (PUT `/users/{user_id}`), "Excluir" (DELETE `/users/{user_id}`).
- **Interações**:
  - Clique em "Adicionar" abre formulário (POST `/users/`).
  - Clique em "Editar" carrega dados do usuário.
  - Clique em "Excluir" remove usuário após confirmação.
- **Estilo**:
  - Botões: Verde (Adicionar), Azul (Editar), Vermelho (Excluir).

### 1.4 Registro de Tokens
```
----------------------------------------
| Social Media Metrics - Tokens        |
----------------------------------------
| [Logout]                             |
----------------------------------------
| Plataforma: [Dropdown: X, Instagram] |
| ID da Plataforma: [_______________]  |
| Access Token: [___________________]  |
| [Salvar Token]                       |
----------------------------------------
```
- **Componentes**:
  - Dropdown: Seleção de plataforma.
  - Campo de texto: `platform_user_id`.
  - Campo de texto: `access_token`.
  - Botão: "Salvar Token" (POST `/users/register-token/`).
- **Interações**:
  - Clique em "Salvar Token" envia dados e exibe confirmação.
  - Exibe erro se token inválido.
- **Estilo**:
  - Botão: Azul (#1976D2).

### 1.5 Consentimento LGPD
```
----------------------------------------
| Social Media Metrics - Consentimento |
----------------------------------------
| [Logout]                             |
----------------------------------------
| [ ] Concordo com a coleta de dados   |
| [Enviar Consentimento]               |
----------------------------------------
```
- **Componentes**:
  - Checkbox: Consentimento.
  - Botão: "Enviar Consentimento" (POST `/consent/`).
- **Interações**:
  - Clique em "Enviar" registra consentimento e exibe confirmação.
- **Estilo**:
  - Botão: Verde (#4CAF50).

## 2. Documentação Swagger

O FastAPI gera automaticamente documentação interativa via **Swagger UI**, acessível em `/docs` (Tarefa 48 dos prompts). Abaixo estão orientações para configurá-la e usá-la.

### 2.1 Configuração
- **Prompt Relacionado** (Tarefa 48):
  - "Use o Cursor Ask para gerar documentação automática da API no README.md, explicando como acessar o Swagger UI em `/docs`."
- **Código no FastAPI**:
  - O FastAPI inclui Swagger UI por padrão. No `app/main.py`:
    ```python
    from fastapi import FastAPI
    app = FastAPI(title="Social Media Metrics API", version="0.1.0")
    ```
  - O parâmetro `title` define o nome da documentação.
- **Acesso**:
  - Inicie o servidor: `./run.sh` (Tarefa 12).
  - Acesse `http://localhost:8000/docs`.

### 2.2 Funcionalidades do Swagger
- **Endpoints Documentados**:
  - `/users/` (POST, GET, PUT, DELETE)
  - `/platforms/` (POST, GET)
  - `/metrics/` (POST, GET)
  - `/users/register-token/` (POST)
  - `/users/{user_id}/tokens/` (GET)
  - `/auth/login` (POST)
  - `/consent/` (POST)
  - `/health` (GET)
- **Interações**:
  - Teste endpoints diretamente no Swagger (ex.: envie POST `/users/` com JSON).
  - Visualize esquemas Pydantic (ex.: modelo de `User`).
  - Baixe o schema OpenAPI em JSON (`/openapi.json`).
- **Exemplo de Uso**:
  - Acesse `/docs`.
  - Clique em POST `/users/register-token/`.
  - Preencha o corpo da requisição:
    ```json
    {
      "platform_user_id": "123456789",
      "access_token": "abc123xyz",
      "platform_id": 3
    }
    ```
  - Clique em "Execute" para testar.

### 2.3 Integração com Frontend
- O frontend não depende do Swagger, mas desenvolvedores podem usar `/docs` para entender a API antes de implementar requisições (ex.: `axios.get('/metrics/')`).
- Inclua no README.md:
  ```markdown
  ## Documentação da API
  Acesse a documentação interativa em `http://localhost:8000/docs` após iniciar o servidor com `./run.sh`.
  ```