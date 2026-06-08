"""replace assignee text with assignee_id FK to members

Revision ID: 20260608_0002
Revises: 20260528_0001
Create Date: 2026-06-08 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260608_0002"
down_revision: Union[str, Sequence[str], None] = "20260528_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # SQLite does not support DROP COLUMN before 3.35, so we recreate the table.
    op.execute("""
        CREATE TABLE tasks_new (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id    INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
            title      TEXT    NOT NULL,
            description TEXT,
            status     TEXT    NOT NULL,
            assignee_id INTEGER REFERENCES members(id) ON DELETE SET NULL,
            created_at TEXT    NOT NULL,
            due_date   TEXT
        )
    """)

    # Migrate existing rows: try to match the old free-text assignee to a member by name.
    # Rows whose assignee text does not match any member name get assignee_id = NULL.
    op.execute("""
        INSERT INTO tasks_new (id, team_id, title, description, status, assignee_id, created_at, due_date)
        SELECT
            t.id,
            t.team_id,
            t.title,
            t.description,
            t.status,
            (SELECT m.id FROM members m WHERE m.name = t.assignee LIMIT 1),
            t.created_at,
            t.due_date
        FROM tasks t
    """)

    op.execute("DROP TABLE tasks")
    op.execute("ALTER TABLE tasks_new RENAME TO tasks")


def downgrade() -> None:
    op.execute("""
        CREATE TABLE tasks_old (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id     INTEGER NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            description TEXT,
            status      TEXT    NOT NULL,
            assignee    TEXT,
            created_at  TEXT    NOT NULL,
            due_date    TEXT
        )
    """)

    op.execute("""
        INSERT INTO tasks_old (id, team_id, title, description, status, assignee, created_at, due_date)
        SELECT
            t.id,
            t.team_id,
            t.title,
            t.description,
            t.status,
            (SELECT m.name FROM members m WHERE m.id = t.assignee_id LIMIT 1),
            t.created_at,
            t.due_date
        FROM tasks t
    """)

    op.execute("DROP TABLE tasks")
    op.execute("ALTER TABLE tasks_old RENAME TO tasks")
