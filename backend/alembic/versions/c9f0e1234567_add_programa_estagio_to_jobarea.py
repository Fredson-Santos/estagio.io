"""Add PROGRAMA_ESTAGIO to jobarea enum

Revision ID: c9f0e1234567
Revises: b7e8d9012345
Create Date: 2026-07-25 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c9f0e1234567'
down_revision: Union[str, None] = 'b7e8d9012345'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("ALTER TYPE jobarea ADD VALUE IF NOT EXISTS 'PROGRAMA_ESTAGIO'")


def downgrade() -> None:
    pass
