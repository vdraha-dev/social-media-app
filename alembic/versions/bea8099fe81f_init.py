"""init

Revision ID: bea8099fe81f
Revises:
Create Date: 2026-06-11 19:27:31.131516

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "bea8099fe81f"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
