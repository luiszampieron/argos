# Argos - Como rodar backend e frontend

Guia simples para rodar os dois projetos localmente.

## Pre-requisitos

- Python 3.11 a 3.13
- uv instalado
- Node.js 18+
- npm

## Exemplo de env

### Backend (`backend/.env`)

```env
APP_ENV=development
ARGOS_DB_PATH=./data/argos.db
ARGOS_JWT_SECRET=troque-por-um-segredo-forte
ARGOS_JWT_ALGORITHM=HS256
ARGOS_TOKEN_EXP_MINUTES=60
ARGOS_API_HOST=127.0.0.1
ARGOS_API_PORT=8001
ARGOS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Frontend (`frontend/.env.local`)

```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8001/api
```

## 1) Subir o backend

No terminal 1:

```bash
cd backend
uv sync --group dev
cp .env.example .env
uv run alembic upgrade head
uv run uvicorn main:app --host 127.0.0.1 --port 8001 --reload
```

Backend em: http://127.0.0.1:8001  
Docs da API em: http://127.0.0.1:8001/docs

## 2) Subir o frontend

No terminal 2:

```bash
cd frontend
npm install
npm run dev
```

Frontend em: http://localhost:3000

## Observação

O frontend deve apontar para a API em `http://127.0.0.1:8001`.
