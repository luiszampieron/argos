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

    app = FastAPI(title="Argos Task Control API", version="0.1.0")

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
