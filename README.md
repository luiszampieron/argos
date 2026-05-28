# Argos API

Core de um sistema de controle de tarefas para equipes, construído com FastAPI, SQLite e organização em DDD.

## Stack

- Python 3.11 a 3.13
- FastAPI
- SQLite
- uv (gerenciamento de ambiente e dependências)

## Arquitetura (DDD)

A estrutura principal está organizada em camadas:

- `src/domain`: regras de domínio, entidades, enums e contratos de repositório
- `src/application`: casos de uso/serviços de aplicação
- `src/infrastructure`: persistência SQLite e implementação dos repositórios
- `src/interfaces/api`: schemas e rotas HTTP
- `src/main.py`: composição da aplicação FastAPI

## Requisitos

- `uv` instalado
- Python compatível (`>=3.11,<3.14`)

## Como rodar

Na raiz do projeto:

```bash
uv sync
```

Suba a API:

```bash
uv run uvicorn main:app --app-dir src --host 127.0.0.1 --port 8001 --reload
```

Observacao:

- O app deve ser iniciado com `--app-dir src`, pois os imports estao relativos ao diretorio `src`.
- Se preferir usar a porta 8000, troque `--port 8001` por `--port 8000`.

## Endpoints principais

- `GET /health`
- `POST /api/teams`
- `GET /api/teams`
- `POST /api/tasks`
- `GET /api/teams/{team_id}/tasks`
- `PATCH /api/tasks/{task_id}/status`

Swagger UI:

- `http://127.0.0.1:8001/docs`

## Exemplos rapidos

Criar equipe:

```bash
curl -X POST "http://127.0.0.1:8001/api/teams" \
  -H "Content-Type: application/json" \
  -d '{"name":"Backend Team"}'
```

Criar tarefa:

```bash
curl -X POST "http://127.0.0.1:8001/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "team_id": 1,
    "title": "Criar endpoint de tarefas",
    "description": "Implementar listagem por equipe",
    "assignee": "Luis"
  }'
```

Atualizar status da tarefa:

```bash
curl -X PATCH "http://127.0.0.1:8001/api/tasks/1/status" \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}'
```

## Banco de dados

O banco SQLite e criado automaticamente em:

- `./data/argos.db`

Pode alterar o caminho com a variavel de ambiente `ARGOS_DB_PATH`.
