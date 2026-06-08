from datetime import datetime, UTC

from pydantic import BaseModel, Field, field_validator

from src.domain.enums import TaskPriority, TaskStatus


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
    priority: TaskPriority = TaskPriority.MEDIUM
    assignee_id: int  # required — every task must have an assignee
    due_date: datetime

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.now(UTC):
            raise ValueError("O prazo deve ser uma data futura")
        return v


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus


class TaskAssigneeUpdateRequest(BaseModel):
    assignee_id: int  # required — removing assignee is not allowed


class TaskResponse(BaseModel):
    id: int
    team_id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    assignee_id: int | None
    assignee_name: str | None
    created_at: datetime
    due_date: datetime | None


class MemberCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=255)
    cargo: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class MemberLoginRequest(BaseModel):
    email: str
    password: str


class MemberResponse(BaseModel):
    id: int
    name: str
    email: str
    cargo: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
