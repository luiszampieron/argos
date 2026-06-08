from src.domain.entities import Member, Task, Team
from src.domain.enums import TaskPriority, TaskStatus
from src.infrastructure.sqlite import SQLiteDatabase, from_iso, to_iso


class SQLiteTeamRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def add(self, team: Team) -> Team:
        with self._database.connection() as conn:
            cursor = conn.execute(
                "INSERT INTO teams(name, created_at) VALUES(?, ?)",
                (team.name, to_iso(team.created_at)),
            )
            team_id = int(cursor.lastrowid)

        return Team(id=team_id, name=team.name, created_at=team.created_at)

    def get(self, team_id: int) -> Team | None:
        with self._database.connection() as conn:
            row = conn.execute(
                "SELECT id, name, created_at FROM teams WHERE id = ?", (
                    team_id,)
            ).fetchone()

        if row is None:
            return None

        return Team(
            id=row["id"],
            name=row["name"],
            created_at=from_iso(row["created_at"]),
        )

    def list_all(self) -> list[Team]:
        with self._database.connection() as conn:
            rows = conn.execute(
                "SELECT id, name, created_at FROM teams ORDER BY id").fetchall()

        teams: list[Team] = []
        for row in rows:
            teams.append(
                Team(
                    id=row["id"],
                    name=row["name"],
                    created_at=from_iso(row["created_at"]),
                )
            )
        return teams


_TASK_SELECT = (
    "SELECT t.id, t.team_id, t.title, t.description, t.status, t.priority,"
    " t.assignee_id, m.name AS assignee_name, t.created_at, t.due_date"
    " FROM tasks t LEFT JOIN members m ON t.assignee_id = m.id"
)


class SQLiteTaskRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def add(self, task: Task) -> Task:
        with self._database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks(team_id, title, description, status, priority, assignee_id, created_at, due_date)
                VALUES(?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.team_id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.priority.value,
                    task.assignee_id,
                    to_iso(task.created_at),
                    to_iso(task.due_date),
                ),
            )
            task_id = int(cursor.lastrowid)

        # Re-fetch to populate assignee_name via JOIN
        return self.get(task_id) or Task(
            id=task_id,
            team_id=task.team_id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            assignee_id=task.assignee_id,
            assignee_name=None,
            created_at=task.created_at,
            due_date=task.due_date,
        )

    def get(self, task_id: int) -> Task | None:
        with self._database.connection() as conn:
            row = conn.execute(
                _TASK_SELECT + " WHERE t.id = ?",
                (task_id,),
            ).fetchone()

        return _to_task(row)

    def list_by_team(self, team_id: int) -> list[Task]:
        with self._database.connection() as conn:
            rows = conn.execute(
                _TASK_SELECT + " WHERE t.team_id = ? ORDER BY t.id",
                (team_id,),
            ).fetchall()

        tasks: list[Task] = []
        for row in rows:
            task = _to_task(row)
            if task is not None:
                tasks.append(task)
        return tasks

    def update_status(self, task_id: int, status: TaskStatus) -> Task | None:
        with self._database.connection() as conn:
            conn.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (status.value, task_id),
            )
            row = conn.execute(
                _TASK_SELECT + " WHERE t.id = ?",
                (task_id,),
            ).fetchone()

        return _to_task(row)

    def update_assignee(self, task_id: int, assignee_id: int | None) -> Task | None:
        with self._database.connection() as conn:
            conn.execute(
                "UPDATE tasks SET assignee_id = ? WHERE id = ?",
                (assignee_id, task_id),
            )
            row = conn.execute(
                _TASK_SELECT + " WHERE t.id = ?",
                (task_id,),
            ).fetchone()

        return _to_task(row)


def _to_task(row: object) -> Task | None:
    if row is None:
        return None

    created_at = from_iso(row["created_at"])
    if created_at is None:
        return None

    return Task(
        id=row["id"],
        team_id=row["team_id"],
        title=row["title"],
        description=row["description"],
        status=TaskStatus(row["status"]),
        priority=TaskPriority(row["priority"]),
        assignee_id=row["assignee_id"],
        assignee_name=row["assignee_name"],
        created_at=created_at,
        due_date=from_iso(row["due_date"]),
    )


class SQLiteMemberRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def add(self, member: Member) -> Member:
        with self._database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO members(name, email, cargo, password_hash, created_at)
                VALUES(?, ?, ?, ?, ?)
                """,
                (
                    member.name,
                    member.email,
                    member.cargo,
                    member.password_hash,
                    to_iso(member.created_at),
                ),
            )
            member_id = int(cursor.lastrowid)

        return Member(
            id=member_id,
            name=member.name,
            email=member.email,
            cargo=member.cargo,
            password_hash=member.password_hash,
            created_at=member.created_at,
        )

    def get_by_id(self, member_id: int) -> Member | None:
        with self._database.connection() as conn:
            row = conn.execute(
                """
                SELECT id, name, email, cargo, password_hash, created_at
                FROM members WHERE id = ?
                """,
                (member_id,),
            ).fetchone()
        return _to_member(row)

    def get_by_email(self, email: str) -> Member | None:
        with self._database.connection() as conn:
            row = conn.execute(
                """
                SELECT id, name, email, cargo, password_hash, created_at
                FROM members WHERE email = ?
                """,
                (email,),
            ).fetchone()
        return _to_member(row)

    def list_all(self) -> list[Member]:
        with self._database.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, name, email, cargo, password_hash, created_at
                FROM members ORDER BY name
                """
            ).fetchall()
        members: list[Member] = []
        for row in rows:
            m = _to_member(row)
            if m is not None:
                members.append(m)
        return members


def _to_member(row: object) -> Member | None:
    if row is None:
        return None

    created_at = from_iso(row["created_at"])
    if created_at is None:
        return None

    return Member(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        cargo=row["cargo"],
        password_hash=row["password_hash"],
        created_at=created_at,
    )
