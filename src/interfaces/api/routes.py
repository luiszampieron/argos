from fastapi import APIRouter, HTTPException, status

from application.exceptions import TaskNotFoundError, TeamNotFoundError
from application.services import TaskManagementService
from interfaces.api.schemas import (
    TaskCreateRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
    TeamCreateRequest,
    TeamResponse,
)


def build_router(service: TaskManagementService) -> APIRouter:
    router = APIRouter(prefix="/api", tags=["tasks"])

    @router.post("/teams", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
    def create_team(payload: TeamCreateRequest) -> TeamResponse:
        team = service.create_team(name=payload.name)
        return TeamResponse.model_validate(team, from_attributes=True)

    @router.get("/teams", response_model=list[TeamResponse])
    def list_teams() -> list[TeamResponse]:
        teams = service.list_teams()
        return [TeamResponse.model_validate(item, from_attributes=True) for item in teams]

    @router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
    def create_task(payload: TaskCreateRequest) -> TaskResponse:
        try:
            task = service.create_task(
                team_id=payload.team_id,
                title=payload.title,
                description=payload.description,
                assignee=payload.assignee,
                due_date=payload.due_date,
            )
        except TeamNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return TaskResponse.model_validate(task, from_attributes=True)

    @router.get("/teams/{team_id}/tasks", response_model=list[TaskResponse])
    def list_tasks_by_team(team_id: int) -> list[TaskResponse]:
        try:
            tasks = service.list_tasks_by_team(team_id)
        except TeamNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return [TaskResponse.model_validate(item, from_attributes=True) for item in tasks]

    @router.patch("/tasks/{task_id}/status", response_model=TaskResponse)
    def update_task_status(task_id: int, payload: TaskStatusUpdateRequest) -> TaskResponse:
        try:
            task = service.update_task_status(task_id, payload.status)
        except TaskNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return TaskResponse.model_validate(task, from_attributes=True)

    return router
