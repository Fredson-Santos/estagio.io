"""Add is_featured to jobs

Revision ID: b7e8d9012345
Revises: e8a0df61067b
Create Date: 2026-07-23 19:10:16.886590

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e8d9012345'
down_revision: Union[str, None] = 'e8a0df61067b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('jobs', sa.Column('is_featured', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column('jobs', 'is_featured')
