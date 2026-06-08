import os

from fastapi import FastAPI

from application.services import AuthService, TaskManagementService
from infrastructure.sqlite import SQLiteDatabase
from infrastructure.sqlite_repositories import (
    SQLiteMemberRepository,
    SQLiteTaskRepository,
    SQLiteTeamRepository,
)
from interfaces.api.routes import build_router


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
        team_repository=team_repo, task_repository=task_repo)
    auth_service = AuthService(
        member_repository=member_repo,
        jwt_secret=jwt_secret,
        token_expiration_minutes=token_exp_minutes,
        jwt_algorithm=jwt_algorithm,
    )

    app = FastAPI(title="Argos Task Control API", version="0.1.0")
    app.include_router(build_router(task_service, auth_service))

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
