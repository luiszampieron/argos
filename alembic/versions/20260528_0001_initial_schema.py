"""initial schema

Revision ID: 20260528_0001
Revises:
Create Date: 2026-05-28 00:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "20260528_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "teams" not in existing_tables:
        op.create_table(
            "teams",
            sa.Column("id", sa.Integer(), primary_key=True,
                      autoincrement=True),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("created_at", sa.Text(), nullable=False),
        )

    if "members" not in existing_tables:
        op.create_table(
            "members",
            sa.Column("id", sa.Integer(), primary_key=True,
                      autoincrement=True),
            sa.Column("name", sa.Text(), nullable=False),
            sa.Column("email", sa.Text(), nullable=False, unique=True),
            sa.Column("cargo", sa.Text(), nullable=False),
            sa.Column("password_hash", sa.Text(), nullable=False),
            sa.Column("created_at", sa.Text(), nullable=False),
        )

    if "tasks" not in existing_tables:
        op.create_table(
            "tasks",
            sa.Column("id", sa.Integer(), primary_key=True,
                      autoincrement=True),
            sa.Column("team_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.Text(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.Text(), nullable=False),
            sa.Column("assignee", sa.Text(), nullable=True),
            sa.Column("created_at", sa.Text(), nullable=False),
            sa.Column("due_date", sa.Text(), nullable=True),
            sa.ForeignKeyConstraint(
                ["team_id"], ["teams.id"], ondelete="CASCADE"),
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    if "tasks" in existing_tables:
        op.drop_table("tasks")
    if "members" in existing_tables:
        op.drop_table("members")
    if "teams" in existing_tables:
        op.drop_table("teams")
