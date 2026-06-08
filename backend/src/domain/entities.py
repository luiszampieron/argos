from dataclasses import dataclass
from datetime import UTC, datetime

from src.domain.enums import TaskPriority, TaskStatus


@dataclass(slots=True)
class Team:
    id: int | None
    name: str
    created_at: datetime


@dataclass(slots=True)
class Member:
    id: int | None
    name: str
    email: str
    cargo: str
    password_hash: str
    created_at: datetime


@dataclass(slots=True)
class Task:
    id: int | None
    team_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee_id: int | None
    # Populated by infrastructure JOIN — not persisted directly.
    assignee_name: str | None
    created_at: datetime
    due_date: datetime | None

    @classmethod
    def create(
        cls,
        team_id: int,
        title: str,
        description: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: int | None = None,
        due_date: datetime | None = None,
    ) -> "Task":
        return cls(
            id=None,
            team_id=team_id,
            title=title,
            description=description,
            status=TaskStatus.TODO,
            priority=priority,
            assignee_id=assignee_id,
            assignee_name=None,
            created_at=datetime.now(UTC),
            due_date=due_date,
        )
