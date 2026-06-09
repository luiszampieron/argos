# Argos API

Backend para controle de tarefas de equipe com FastAPI, SQLite e organizacao em DDD.

## Objetivo

Este repositorio implementa a base de uma API para:

- cadastro e autenticacao de membros
- cadastro e consulta de equipes
- cadastro e acompanhamento de tarefas
- controle de status das tarefas

## Stack

- Python 3.11 ate 3.13
- FastAPI
- SQLite
- Alembic (migrations)
- uv (ambiente e dependencias)

## Estrutura do projeto

- src/domain: entidades, enums e contratos de repositorio
- src/application: servicos e regras de negocio
- src/infrastructure: persistencia SQLite e implementacoes de repositorio
- src/interfaces/api: contratos HTTP (schemas) e rotas
- src/main.py: bootstrap da aplicacao
- alembic: configuracao e historico de migrations

## Requisitos

- uv instalado
- Python compativel com o projeto

## Setup local

1. Instalar dependencias da aplicacao

uv sync

2. Instalar dependencias de desenvolvimento (inclui Alembic)

uv sync --group dev

3. Criar o arquivo de ambiente a partir do template

cp .env.example .env

4. Carregar variaveis do .env no shell atual

set -a
source .env
set +a

5. Aplicar migrations

uv run alembic upgrade head

## Executar a API

uv run uvicorn main:app --host 127.0.0.1 --port 8001 --reload

Notas:

- use --app-dir src para resolucao correta dos imports
- ajuste host e porta conforme sua necessidade
- docs interativa: http://127.0.0.1:8001/docs

## Variaveis de ambiente

Definidas em .env.example:

- APP_ENV: ambiente de execucao (exemplo: development)
- ARGOS_DB_PATH: caminho do banco SQLite
- ARGOS_JWT_SECRET: segredo para assinatura dos tokens
- ARGOS_JWT_ALGORITHM: algoritmo JWT (padrao HS256)
- ARGOS_TOKEN_EXP_MINUTES: expiracao do token em minutos
- ARGOS_API_HOST: host sugerido para executar a API
- ARGOS_API_PORT: porta sugerida para executar a API

## Endpoints

Publicos:

- GET /health
- POST /api/auth/register
- POST /api/auth/login

Protegidos por Bearer Token:

- GET /api/auth/me
- POST /api/teams
- GET /api/teams
- POST /api/tasks
- GET /api/teams/{team_id}/tasks
- PATCH /api/tasks/{task_id}/status

## Fluxo rapido de autenticacao

1. Registrar membro

curl -X POST "http://127.0.0.1:8001/api/auth/register" \
 -H "Content-Type: application/json" \
 -d '{"name":"Luis","email":"luis@example.com","cargo":"Backend Dev","password":"Senha@123"}'

2. Fazer login e receber access_token

curl -X POST "http://127.0.0.1:8001/api/auth/login" \
 -H "Content-Type: application/json" \
 -d '{"email":"luis@example.com","password":"Senha@123"}'

3. Usar token no header Authorization

Authorization: Bearer SEU_TOKEN

## Regras atuais de senha

- minimo de 8 caracteres
- ao menos 1 letra maiuscula
- ao menos 1 letra minuscula
- ao menos 1 numero
- ao menos 1 caractere especial

## Migrations

Comandos principais:

- aplicar pendencias: uv run alembic upgrade head
- criar migration: uv run alembic revision -m "descricao"
- ver revisao atual: uv run alembic current
- voltar uma revisao: uv run alembic downgrade -1

Importante:

- o startup da API nao cria tabelas automaticamente
- rode migrations antes de iniciar a API

## Estado funcional atual

O projeto esta operacional para autenticacao, equipes e tarefas basicas.

Itens que ainda podem ser evoluidos para aderencia total ao enunciado da atividade:

- prioridade da tarefa (baixa/media/alta)
- responsavel obrigatorio por tarefa
- buscar tarefa por id
- atualizar responsavel da tarefa
- filtrar tarefas por responsavel
- filtrar tarefas por status

## Documentacao complementar

- docs/API_REFERENCE.md
- docs/DEVELOPMENT.md
