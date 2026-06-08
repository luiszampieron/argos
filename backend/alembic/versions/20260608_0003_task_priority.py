"""add priority column to tasks

Revision ID: 20260608_0003
Revises: 20260608_0002
Create Date: 2026-06-08 00:00:00.000000
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260608_0003"
down_revision: Union[str, Sequence[str], None] = "20260608_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    cols = {row[1] for row in bind.execute(sa.text("PRAGMA table_info(tasks)"))}
    if "priority" not in cols:
        op.execute(
            "ALTER TABLE tasks ADD COLUMN priority TEXT NOT NULL DEFAULT 'medium'")


def downgrade() -> None:
    # SQLite <3.35 cannot drop columns; recreate without it.
    op.execute("""
        CREATE TABLE tasks_no_priority AS
        SELECT id, team_id, title, description, status, assignee_id, created_at, due_date
        FROM tasks
    """)
    op.execute("DROP TABLE tasks")
    op.execute("""
        CREATE TABLE tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id     INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            description TEXT,
            status      TEXT    NOT NULL,
            assignee_id INTEGER REFERENCES members(id) ON DELETE SET NULL,
            created_at  TEXT    NOT NULL,
            due_date    TEXT
        )
    """)
    op.execute("INSERT INTO tasks SELECT * FROM tasks_no_priority")
    op.execute("DROP TABLE tasks_no_priority")
