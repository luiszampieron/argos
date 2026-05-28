from datetime import datetime

from pydantic import BaseModel, Field

from domain.enums import TaskStatus


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class TeamResponse(BaseModel):
    id: int
    name: str
    created_at: datetime


class TaskCreateRequest(BaseModel):
    team_id: int
    title: str = Field(min_length=2, max_length=200)
    description: str | None = None
    assignee: str | None = Field(default=None, max_length=120)
    due_date: datetime | None = None


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus


class TaskResponse(BaseModel):
    id: int
    team_id: int
    title: str
    description: str | None
    status: TaskStatus
    assignee: str | None
    created_at: datetime
    due_date: datetime | None
