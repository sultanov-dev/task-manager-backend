"""refresh token model

Revision ID: 633d99adc338
Revises: 28c6812a546f
Create Date: 2026-10-09 18:18:30.672546

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '633d99adc338'
down_revision: Union[str, Sequence[str], None] = '28c6812a546f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
