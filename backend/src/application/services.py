import re
from datetime import timedelta
from datetime import UTC, datetime

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from src.application.exceptions import (
    InvalidCredentialsError,
    InvalidTaskOperationError,
    InvalidTokenError,
    MemberAlreadyExistsError,
    MemberNotFoundError,
    TaskNotFoundError,
    TeamNotFoundError,
    WeakPasswordError,
)
from src.domain.entities import Member, Task, Team
from src.domain.enums import TaskPriority, TaskStatus
from src.domain.repositories import MemberRepository, TaskRepository, TeamRepository


class TaskManagementService:
    def __init__(
        self,
        team_repository: TeamRepository,
        task_repository: TaskRepository,
        member_repository: MemberRepository,
    ) -> None:
        self._team_repository = team_repository
        self._task_repository = task_repository
        self._member_repository = member_repository

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
        priority: TaskPriority = TaskPriority.MEDIUM,
        assignee_id: int | None = None,
        due_date: datetime | None = None,
    ) -> Task:
        if self._team_repository.get(team_id) is None:
            raise TeamNotFoundError(f"Team {team_id} not found")

        task = Task.create(
            team_id=team_id,
            title=title,
            description=description,
            priority=priority,
            assignee_id=assignee_id,
            due_date=due_date,
        )
        return self._task_repository.add(task)

    def list_tasks_by_team(self, team_id: int) -> list[Task]:
        if self._team_repository.get(team_id) is None:
            raise TeamNotFoundError(f"Team {team_id} not found")
        return self._task_repository.list_by_team(team_id)

    def get_task(self, task_id: int) -> Task:
        task = self._task_repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return task

    def update_task_status(self, task_id: int, status: TaskStatus) -> Task:
        task = self._task_repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        if status == TaskStatus.DONE and task.assignee_id is None:
            raise InvalidTaskOperationError(
                "Não é possível concluir uma tarefa sem responsável"
            )
        updated = self._task_repository.update_status(task_id, status)
        if updated is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return updated

    def update_task_assignee(self, task_id: int, assignee_id: int) -> Task:
        if self._task_repository.get(task_id) is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        updated = self._task_repository.update_assignee(task_id, assignee_id)
        if updated is None:
            raise TaskNotFoundError(f"Task {task_id} not found")
        return updated

    def list_members(self) -> list[Member]:
        return self._member_repository.list_all()


class AuthService:
    def __init__(
        self,
        member_repository: MemberRepository,
        jwt_secret: str,
        token_expiration_minutes: int = 60,
        jwt_algorithm: str = "HS256",
    ) -> None:
        self._member_repository = member_repository
        self._jwt_secret = jwt_secret
        self._token_expiration_minutes = token_expiration_minutes
        self._jwt_algorithm = jwt_algorithm
        self._password_hasher = PasswordHasher()

    def register_member(self, name: str, email: str, cargo: str, password: str) -> Member:
        normalized_email = email.strip().lower()
        self._validate_password_strength(password)

        if self._member_repository.get_by_email(normalized_email) is not None:
            raise MemberAlreadyExistsError("E-mail already in use")

        member = Member(
            id=None,
            name=name.strip(),
            email=normalized_email,
            cargo=cargo.strip(),
            password_hash=self._password_hasher.hash(password),
            created_at=datetime.now(UTC),
        )
        return self._member_repository.add(member)

    def authenticate(self, email: str, password: str) -> str:
        normalized_email = email.strip().lower()
        member = self._member_repository.get_by_email(normalized_email)
        if member is None:
            raise InvalidCredentialsError("Invalid e-mail or password")

        try:
            is_valid = self._password_hasher.verify(
                member.password_hash, password)
        except (VerifyMismatchError, InvalidHashError) as exc:
            raise InvalidCredentialsError(
                "Invalid e-mail or password") from exc

        if not is_valid:
            raise InvalidCredentialsError("Invalid e-mail or password")

        expires_at = datetime.now(
            UTC) + timedelta(minutes=self._token_expiration_minutes)
        payload = {
            "sub": str(member.id),
            "email": member.email,
            "exp": expires_at,
        }
        return jwt.encode(payload, self._jwt_secret, algorithm=self._jwt_algorithm)

    def get_member_from_token(self, token: str) -> Member:
        try:
            payload = jwt.decode(token, self._jwt_secret,
                                 algorithms=[self._jwt_algorithm])
        except jwt.InvalidTokenError as exc:
            raise InvalidTokenError("Invalid or expired token") from exc

        subject = payload.get("sub")
        if subject is None:
            raise InvalidTokenError("Invalid token payload")

        try:
            member_id = int(subject)
        except (TypeError, ValueError) as exc:
            raise InvalidTokenError("Invalid token payload") from exc

        member = self._member_repository.get_by_id(member_id)
        if member is None:
            raise MemberNotFoundError("Member not found")
        return member

    @staticmethod
    def _validate_password_strength(password: str) -> None:
        if len(password) < 8:
            raise WeakPasswordError("Password must have at least 8 characters")
        if not re.search(r"[A-Z]", password):
            raise WeakPasswordError(
                "Password must contain an uppercase letter")
        if not re.search(r"[a-z]", password):
            raise WeakPasswordError("Password must contain a lowercase letter")
        if not re.search(r"\d", password):
            raise WeakPasswordError("Password must contain a number")
        if not re.search(r"[^A-Za-z0-9]", password):
            raise WeakPasswordError(
                "Password must contain a special character")
