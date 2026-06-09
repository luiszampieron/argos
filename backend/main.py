import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.application.services import AuthService, TaskManagementService
from src.infrastructure.sqlite import SQLiteDatabase
from src.infrastructure.sqlite_repositories import (
    SQLiteMemberRepository,
    SQLiteTaskRepository,
    SQLiteTeamRepository,
)
from src.interfaces.api.routes import build_router


_OPENAPI_TAGS: list[dict] = [
    {
        "name": "auth",
        "description": (
            "Registro e autenticação de membros. "
            "O token JWT retornado em `/auth/login` deve ser enviado como "
            "`Authorization: Bearer <token>` em todas as demais rotas."
        ),
    },
    {
        "name": "teams",
        "description": "Criação e listagem de equipes.",
    },
    {
        "name": "tasks",
        "description": (
            "Gerenciamento do ciclo de vida das tarefas: criação, consulta, "
            "atualização de status (`todo → in_progress → done / blocked`) "
            "e reatribuição de responsável."
        ),
    },
    {
        "name": "members",
        "description": "Consulta de membros cadastrados na plataforma.",
    },
    {
        "name": "system",
        "description": "Endpoints de infraestrutura/saúde da aplicação.",
    },
]

_DESCRIPTION = """
## Argos Task Control API

API RESTful para gerenciamento de tarefas em equipe.

### Fluxo básico

1. **Registre** um membro em `POST /api/auth/register`.
2. **Autentique-se** em `POST /api/auth/login` e obtenha o `access_token`.
3. Envie o header `Authorization: Bearer <token>` em todas as demais requisições.
4. Crie uma **equipe** (`POST /api/teams`) e depois crie **tarefas** (`POST /api/tasks`).
5. Avance o status das tarefas com `PATCH /api/tasks/{id}/status`.

### Transições de status permitidas

| De | Para |
|----|------|
| `todo` | `in_progress`, `blocked` |
| `in_progress` | `done`, `blocked` |
| `blocked` | `in_progress` |

### Autenticação

Todas as rotas (exceto `/api/auth/register`, `/api/auth/login` e `/health`) exigem
um token JWT no header:

```
Authorization: Bearer <token>
```
"""


def create_app() -> FastAPI:
    db_path = os.getenv("ARGOS_DB_PATH", "./data/argos.db")
    jwt_secret = os.getenv("ARGOS_JWT_SECRET", "change-this-in-production")
    jwt_algorithm = os.getenv("ARGOS_JWT_ALGORITHM", "HS256")
    token_exp_minutes = int(os.getenv("ARGOS_TOKEN_EXP_MINUTES", "60"))
    database = SQLiteDatabase(db_path=db_path)

    team_repo = SQLiteTeamRepository(database)
    task_repo = SQLiteTaskRepository(database)
    member_repo = SQLiteMemberRepository(database)

    task_service = TaskManagementService(
        team_repository=team_repo,
        task_repository=task_repo,
        member_repository=member_repo,
    )
    auth_service = AuthService(
        member_repository=member_repo,
        jwt_secret=jwt_secret,
        token_expiration_minutes=token_exp_minutes,
        jwt_algorithm=jwt_algorithm,
    )

    app = FastAPI(
        title="Argos Task Control API",
        version="0.1.0",
        description=_DESCRIPTION,
        openapi_tags=_OPENAPI_TAGS,
        contact={"name": "Argos Dev Team"},
        license_info={"name": "MIT"},
    )

    allowed_origins = os.getenv(
        "ARGOS_ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(build_router(task_service, auth_service))

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
