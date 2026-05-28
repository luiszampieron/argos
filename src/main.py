import os

from fastapi import FastAPI

from application.services import TaskManagementService
from infrastructure.sqlite import SQLiteDatabase
from infrastructure.sqlite_repositories import SQLiteTaskRepository, SQLiteTeamRepository
from interfaces.api.routes import build_router


def create_app() -> FastAPI:
    db_path = os.getenv("ARGOS_DB_PATH", "./data/argos.db")
    database = SQLiteDatabase(db_path=db_path)
    database.initialize_schema()

    team_repo = SQLiteTeamRepository(database)
    task_repo = SQLiteTaskRepository(database)
    service = TaskManagementService(
        team_repository=team_repo, task_repository=task_repo)

    app = FastAPI(title="Argos Task Control API", version="0.1.0")
    app.include_router(build_router(service))

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    return app


app = create_app()
