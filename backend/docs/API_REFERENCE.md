# API Reference

Base URL local:

http://127.0.0.1:8001

Autenticacao:

- tipo: Bearer token
- header: Authorization: Bearer TOKEN

## Health

GET /health

Resposta 200:

{
"status": "ok"
}

## Auth

### POST /api/auth/register

Descricao:

Cria um membro com senha hash via Argon2.

Body:

{
"name": "string",
"email": "string",
"cargo": "string",
"password": "string"
}

Resposta 201:

{
"id": 1,
"name": "string",
"email": "string",
"cargo": "string",
"created_at": "2026-05-28T12:00:00+00:00"
}

Erros comuns:

- 400: senha fraca
- 409: email ja cadastrado

### POST /api/auth/login

Descricao:

Autentica membro e retorna token JWT.

Body:

{
"email": "string",
"password": "string"
}

Resposta 200:

{
"access_token": "jwt-token",
"token_type": "bearer"
}

Erro comum:

- 401: credenciais invalidas

### GET /api/auth/me

Descricao:

Retorna dados do membro autenticado.

Resposta 200:

{
"id": 1,
"name": "string",
"email": "string",
"cargo": "string",
"created_at": "2026-05-28T12:00:00+00:00"
}

Erro comum:

- 401: token ausente, invalido ou expirado

## Teams

### POST /api/teams

Descricao:

Cria uma equipe.

Body:

{
"name": "string"
}

Resposta 201:

{
"id": 1,
"name": "string",
"created_at": "2026-05-28T12:00:00+00:00"
}

### GET /api/teams

Descricao:

Lista equipes cadastradas.

Resposta 200:

[
{
"id": 1,
"name": "string",
"created_at": "2026-05-28T12:00:00+00:00"
}
]

## Tasks

### POST /api/tasks

Descricao:

Cria uma tarefa para uma equipe.

Body:

{
"team_id": 1,
"title": "string",
"description": "string ou null",
"assignee": "string ou null",
"due_date": "2026-06-01T10:00:00+00:00 ou null"
}

Resposta 201:

{
"id": 1,
"team_id": 1,
"title": "string",
"description": "string ou null",
"status": "todo",
"assignee": "string ou null",
"created_at": "2026-05-28T12:00:00+00:00",
"due_date": "2026-06-01T10:00:00+00:00 ou null"
}

Erro comum:

- 404: team nao encontrada

### GET /api/teams/{team_id}/tasks

Descricao:

Lista tarefas da equipe.

Resposta 200:

[
{
"id": 1,
"team_id": 1,
"title": "string",
"description": "string ou null",
"status": "todo",
"assignee": "string ou null",
"created_at": "2026-05-28T12:00:00+00:00",
"due_date": "2026-06-01T10:00:00+00:00 ou null"
}
]

### PATCH /api/tasks/{task_id}/status

Descricao:

Atualiza status da tarefa.

Body:

{
"status": "todo | in_progress | done | blocked"
}

Resposta 200:

{
"id": 1,
"team_id": 1,
"title": "string",
"description": "string ou null",
"status": "done",
"assignee": "string ou null",
"created_at": "2026-05-28T12:00:00+00:00",
"due_date": "2026-06-01T10:00:00+00:00 ou null"
}

Erro comum:

- 404: tarefa nao encontrada
