from datetime import UTC, datetime

from application.exceptions import TaskNotFoundError, TeamNotFoundError
from domain.entities import Task, Team
from domain.enums import TaskStatus
from domain.repositories import TaskRepository, TeamRepository


class TaskManagementService:
    def __init__(self, team_repository: TeamRepository, task_repository: TaskRepository) -> None:
        self._team_repository = team_repository
        self._task_repository = task_repository

    def create_team(self, name: str) -> Team:
        team = Team(id=None, name=name, created_at=datetime.now(UTC))
        return self._team_repository.add(team)

    def list_teams(self) -> list[Team]:
        return self._team_repository.list_all()

    def create_task(
        self,
        team_id: int,
        title: str,
        description: str | None = None,
        assignee: str | None = None,
        due_date: datetime | None = None,
    ) -> Task:
        if self._team_repository.get(team_id) is None:
            raise TeamNotFoundError(f"Team {team_id} not found")

        task = Task.create(
            team_id=team_id,
            title=title,
            description=description,
            assignee=assignee,
            due_date=due_date,
        )
        return self._task_repository.add(task)

    def list_tasks_by_team(self, team_id: int) -> list[Task]:
        if self._team_repository.get(team_id) is None:
            raise TeamNotFoundError(f"Team {team_id} not found")
        return self._task_repository.list_by_team(team_id)

    def update_task_status(self, task_id: int, status: TaskStatus) -> Task:
        updated = self._task_repository.update_status(task_id, status)
        if updated is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return updated
