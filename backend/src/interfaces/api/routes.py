from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

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
from src.application.services import AuthService, TaskManagementService
from src.domain.entities import Member
from src.interfaces.api.schemas import (
    MemberCreateRequest,
    MemberLoginRequest,
    MemberResponse,
    TaskAssigneeUpdateRequest,
    TaskCreateRequest,
    TaskResponse,
    TaskStatusUpdateRequest,
    TokenResponse,
    TeamCreateRequest,
    TeamResponse,
)


_UNAUTH = {401: {"description": "Token ausente, inválido ou expirado"}}
_NOT_FOUND = {404: {"description": "Recurso não encontrado"}}
_UNAUTH_NOT_FOUND = {**_UNAUTH, **_NOT_FOUND}


def build_router(task_service: TaskManagementService, auth_service: AuthService) -> APIRouter:
    router = APIRouter(prefix="/api")
    bearer = HTTPBearer(auto_error=False)

    def current_member(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
    ) -> Member:
        if credentials is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing bearer token",
            )
        try:
            return auth_service.get_member_from_token(credentials.credentials)
        except (InvalidTokenError, MemberNotFoundError) as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
            ) from exc

    @router.post(
        "/auth/register",
        response_model=MemberResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["auth"],
        summary="Registrar novo membro",
        description="Cria uma conta de membro. A senha deve ter no mínimo 8 caracteres.",
        responses={
            409: {"description": "E-mail já cadastrado"},
            400: {"description": "Senha fraca ou dados inválidos"},
        },
    )
    def register_member(payload: MemberCreateRequest) -> MemberResponse:
        try:
            member = auth_service.register_member(
                name=payload.name,
                email=payload.email,
                cargo=payload.cargo,
                password=payload.password,
            )
        except MemberAlreadyExistsError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
        except WeakPasswordError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc

        return MemberResponse.model_validate(member, from_attributes=True)

    @router.post(
        "/auth/login",
        response_model=TokenResponse,
        tags=["auth"],
        summary="Autenticar membro",
        description=(
            "Autentica com e-mail e senha e retorna um token JWT. "
            "Use o token como `Authorization: Bearer <token>` nas demais rotas."
        ),
        responses={401: {"description": "Credenciais inválidas"}},
    )
    def login(payload: MemberLoginRequest) -> TokenResponse:
        try:
            token = auth_service.authenticate(
                email=payload.email, password=payload.password)
        except InvalidCredentialsError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
        return TokenResponse(access_token=token)

    @router.get(
        "/auth/me",
        response_model=MemberResponse,
        tags=["auth"],
        summary="Membro autenticado",
        description="Retorna os dados do membro identificado pelo token JWT.",
        responses=_UNAUTH,
    )
    def me(member: Member = Depends(current_member)) -> MemberResponse:
        return MemberResponse.model_validate(member, from_attributes=True)

    @router.post(
        "/teams",
        response_model=TeamResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["teams"],
        summary="Criar equipe",
        description="Cria uma nova equipe. O nome deve ter entre 2 e 120 caracteres.",
        responses=_UNAUTH,
    )
    def create_team(payload: TeamCreateRequest, _: Member = Depends(current_member)) -> TeamResponse:
        team = task_service.create_team(name=payload.name)
        return TeamResponse.model_validate(team, from_attributes=True)

    @router.get(
        "/teams",
        response_model=list[TeamResponse],
        tags=["teams"],
        summary="Listar equipes",
        description="Retorna todas as equipes cadastradas.",
        responses=_UNAUTH,
    )
    def list_teams(_: Member = Depends(current_member)) -> list[TeamResponse]:
        teams = task_service.list_teams()
        return [TeamResponse.model_validate(item, from_attributes=True) for item in teams]

    @router.post(
        "/tasks",
        response_model=TaskResponse,
        status_code=status.HTTP_201_CREATED,
        tags=["tasks"],
        summary="Criar tarefa",
        description=(
            "Cria uma nova tarefa para uma equipe. "
            "O `due_date` deve ser uma data/hora futura em UTC. "
            "A tarefa inicia com status `todo`."
        ),
        responses={**_UNAUTH, 404: {"description": "Equipe não encontrada"}},
    )
    def create_task(payload: TaskCreateRequest, _: Member = Depends(current_member)) -> TaskResponse:
        try:
            task = task_service.create_task(
                team_id=payload.team_id,
                title=payload.title,
                description=payload.description,
                priority=payload.priority,
                assignee_id=payload.assignee_id,
                due_date=payload.due_date,
            )
        except TeamNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return TaskResponse.model_validate(task, from_attributes=True)

    @router.get(
        "/tasks/{task_id}",
        response_model=TaskResponse,
        tags=["tasks"],
        summary="Buscar tarefa",
        description="Retorna os detalhes de uma tarefa pelo seu ID.",
        responses=_UNAUTH_NOT_FOUND,
    )
    def get_task(task_id: int, _: Member = Depends(current_member)) -> TaskResponse:
        try:
            task = task_service.get_task(task_id)
        except TaskNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return TaskResponse.model_validate(task, from_attributes=True)

    @router.get(
        "/teams/{team_id}/tasks",
        response_model=list[TaskResponse],
        tags=["tasks"],
        summary="Listar tarefas da equipe",
        description="Retorna todas as tarefas de uma equipe específica.",
        responses=_UNAUTH_NOT_FOUND,
    )
    def list_tasks_by_team(team_id: int, _: Member = Depends(current_member)) -> list[TaskResponse]:
        try:
            tasks = task_service.list_tasks_by_team(team_id)
        except TeamNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

        return [TaskResponse.model_validate(item, from_attributes=True) for item in tasks]

    @router.patch(
        "/tasks/{task_id}/assignee",
        response_model=TaskResponse,
        tags=["tasks"],
        summary="Reatribuir responsável",
        description="Altera o membro responsável pela tarefa.",
        responses=_UNAUTH_NOT_FOUND,
    )
    def update_task_assignee(
        task_id: int,
        payload: TaskAssigneeUpdateRequest,
        _: Member = Depends(current_member),
    ) -> TaskResponse:
        try:
            task = task_service.update_task_assignee(
                task_id, payload.assignee_id)
        except TaskNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return TaskResponse.model_validate(task, from_attributes=True)

    @router.get(
        "/members",
        response_model=list[MemberResponse],
        tags=["members"],
        summary="Listar membros",
        description="Retorna todos os membros cadastrados na plataforma.",
        responses=_UNAUTH,
    )
    def list_members(_: Member = Depends(current_member)) -> list[MemberResponse]:
        members = task_service.list_members()
        return [MemberResponse.model_validate(m, from_attributes=True) for m in members]

    @router.patch(
        "/tasks/{task_id}/status",
        response_model=TaskResponse,
        tags=["tasks"],
        summary="Atualizar status da tarefa",
        description=(
            "Avança ou retrocede o status de uma tarefa. "
            "Transições permitidas: `todo → in_progress`, `todo → blocked`, "
            "`in_progress → done`, `in_progress → blocked`, `blocked → in_progress`."
        ),
        responses={
            **_UNAUTH_NOT_FOUND,
            422: {"description": "Transição de status inválida"},
        },
    )
    def update_task_status(
        task_id: int,
        payload: TaskStatusUpdateRequest,
        _: Member = Depends(current_member),
    ) -> TaskResponse:
        try:
            task = task_service.update_task_status(task_id, payload.status)
        except TaskNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        except InvalidTaskOperationError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

        return TaskResponse.model_validate(task, from_attributes=True)

    return router
