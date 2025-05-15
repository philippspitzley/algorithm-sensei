"""change_course_description_to_text

Revision ID: 2f77334a0b4f
Revises: 5c2d4ff10905
Create Date: 2025-05-15 13:05:21.238926

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2f77334a0b4f"
down_revision: str | None = "5c2d4ff10905"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        "course",
        "description",
        existing_type=sa.String(),
        type_=sa.Text(),
        existing_nullable=True,
    )
    op.alter_column(
        "chapter",
        "description",
        existing_type=sa.String(),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "course",
        "description",
        existing_type=sa.Text(),
        type_=sa.String(255),
        existing_nullable=True,
    )
    op.alter_column(
        "chapter",
        "description",
        existing_type=sa.Text(),
        type_=sa.String(255),
        existing_nullable=True,
    )
