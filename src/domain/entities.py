from dataclasses import dataclass
from datetime import UTC, datetime

from domain.enums import TaskStatus


@dataclass(slots=True)
class Team:
    id: int | None
    name: str
    created_at: datetime


@dataclass(slots=True)
class Task:
    id: int | None
    team_id: int
    title: str
    description: str | None
    status: TaskStatus
    assignee: str | None
    created_at: datetime
    due_date: datetime | None

    @classmethod
    def create(
        cls,
        team_id: int,
        title: str,
        description: str | None = None,
        assignee: str | None = None,
        due_date: datetime | None = None,
    ) -> "Task":
        return cls(
            id=None,
            team_id=team_id,
            title=title,
            description=description,
            status=TaskStatus.TODO,
            assignee=assignee,
            created_at=datetime.now(UTC),
            due_date=due_date,
        )
