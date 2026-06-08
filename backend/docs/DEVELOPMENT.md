# Development Guide

## 1) Ambiente

1. Instale uv.
2. Garanta Python 3.11 ate 3.13.
3. Na raiz do repositorio rode:

uv sync --group dev

## 2) Configuracao local

1. Crie o .env a partir do template:

cp .env.example .env

2. Carregue variaveis no shell:

set -a
source .env
set +a

## 3) Banco e migrations

Aplicar migracoes pendentes:

uv run alembic upgrade head

Criar nova migration:

uv run alembic revision -m "descricao da alteracao"

Conferir revisao ativa:

uv run alembic current

## 4) Rodar API

uv run uvicorn main:app --app-dir src --host 127.0.0.1 --port 8001 --reload

## 5) Validacoes rapidas

Compilar codigo:

uv run python -m compileall src

Checar health:

curl http://127.0.0.1:8001/health

## 6) Troubleshooting

Erro ModuleNotFoundError para application/domain/interfaces:

- garanta que usou --app-dir src no uvicorn.

Erro de porta em uso:

- troque para outra porta, exemplo --port 8002.

Erro de token:

- confirme se Authorization esta no formato Bearer TOKEN.

Erro de migration nao aplicada:

- rode uv run alembic upgrade head antes de subir a API.

## 7) Convencoes atuais

- arquitetura em camadas DDD
- SQLite para persistencia local
- alembic para versionamento de schema
- auth JWT com senha hash Argon2
