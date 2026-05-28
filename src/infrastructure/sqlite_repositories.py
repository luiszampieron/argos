from domain.entities import Task, Team
from domain.enums import TaskStatus
from infrastructure.sqlite import SQLiteDatabase, from_iso, to_iso


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


class SQLiteTaskRepository:
    def __init__(self, database: SQLiteDatabase) -> None:
        self._database = database

    def add(self, task: Task) -> Task:
        with self._database.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks(team_id, title, description, status, assignee, created_at, due_date)
                VALUES(?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.team_id,
                    task.title,
                    task.description,
                    task.status.value,
                    task.assignee,
                    to_iso(task.created_at),
                    to_iso(task.due_date),
                ),
            )
            task_id = int(cursor.lastrowid)

        return Task(
            id=task_id,
            team_id=task.team_id,
            title=task.title,
            description=task.description,
            status=task.status,
            assignee=task.assignee,
            created_at=task.created_at,
            due_date=task.due_date,
        )

    def get(self, task_id: int) -> Task | None:
        with self._database.connection() as conn:
            row = conn.execute(
                """
                SELECT id, team_id, title, description, status, assignee, created_at, due_date
                FROM tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()

        return _to_task(row)

    def list_by_team(self, team_id: int) -> list[Task]:
        with self._database.connection() as conn:
            rows = conn.execute(
                """
                SELECT id, team_id, title, description, status, assignee, created_at, due_date
                FROM tasks WHERE team_id = ? ORDER BY id
                """,
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
                """
                SELECT id, team_id, title, description, status, assignee, created_at, due_date
                FROM tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()

        return _to_task(row)


def _to_task(row: object) -> Task | None:
    if row is None:
        return None

    return Task(
        id=row["id"],
        team_id=row["team_id"],
        title=row["title"],
        description=row["description"],
        status=TaskStatus(row["status"]),
        assignee=row["assignee"],
        created_at=from_iso(row["created_at"]),
        due_date=from_iso(row["due_date"]),
    )
