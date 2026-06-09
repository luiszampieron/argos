from datetime import datetime, UTC

from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.domain.enums import TaskPriority, TaskStatus


class TeamCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120,
                      description="Nome da equipe", examples=["Equipe Alpha"])


class TeamResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {"id": 1, "name": "Equipe Alpha", "created_at": "2026-06-01T10:00:00Z"}
        }
    )

    id: int
    name: str
    created_at: datetime


class TaskCreateRequest(BaseModel):
    team_id: int = Field(
        description="ID da equipe à qual a tarefa pertence", examples=[1])
    title: str = Field(min_length=2, max_length=200, description="Título da tarefa", examples=[
                       "Implementar autenticação JWT"])
    description: str | None = Field(default=None, description="Descrição detalhada (opcional)", examples=[
                                    "Adicionar fluxo de login com refresh token"])
    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM, description="Prioridade da tarefa")
    assignee_id: int = Field(
        description="ID do membro responsável", examples=[3])
    due_date: datetime = Field(
        description="Prazo de entrega em UTC (deve ser futuro)", examples=["2026-12-31T23:59:00Z"])

    @field_validator("due_date")
    @classmethod
    def due_date_must_be_future(cls, v: datetime) -> datetime:
        if v <= datetime.now(UTC):
            raise ValueError("O prazo deve ser uma data futura")
        return v


class TaskStatusUpdateRequest(BaseModel):
    status: TaskStatus = Field(description="Novo status da tarefa")


class TaskAssigneeUpdateRequest(BaseModel):
    assignee_id: int = Field(
        description="ID do novo membro responsável", examples=[5])


class TaskResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 42,
                "team_id": 1,
                "title": "Implementar autenticação JWT",
                "description": "Adicionar fluxo de login com refresh token",
                "status": "in_progress",
                "priority": "high",
                "assignee_id": 3,
                "assignee_name": "Maria Silva",
                "created_at": "2026-06-01T10:00:00Z",
                "due_date": "2026-12-31T23:59:00Z",
            }
        }
    )

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
    name: str = Field(min_length=2, max_length=120,
                      description="Nome completo", examples=["Maria Silva"])
    email: str = Field(min_length=5, max_length=255,
                       description="E-mail único", examples=["maria@exemplo.com"])
    cargo: str = Field(min_length=2, max_length=80,
                       description="Cargo ou função", examples=["Desenvolvedora Backend"])
    password: str = Field(min_length=8, max_length=128,
                          description="Senha (mín. 8 caracteres)", examples=["S3nh@Segura!"])


class MemberLoginRequest(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "email": "maria@exemplo.com", "password": "S3nh@Segura!"}}
    )

    email: str = Field(description="E-mail cadastrado",
                       examples=["maria@exemplo.com"])
    password: str = Field(description="Senha da conta",
                          examples=["S3nh@Segura!"])


class MemberResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 3,
                "name": "Maria Silva",
                "email": "maria@exemplo.com",
                "cargo": "Desenvolvedora Backend",
                "created_at": "2026-06-01T09:00:00Z",
            }
        }
    )

    id: int
    name: str
    email: str
    cargo: str
    created_at: datetime


class TokenResponse(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"example": {
            "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "token_type": "bearer"}}
    )

    access_token: str = Field(description="Token JWT de acesso")
    token_type: str = Field(
        default="bearer", description="Tipo do token (sempre 'bearer')")
