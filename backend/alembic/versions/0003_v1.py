"""v1 - revision stamp

Revision ID: 0003_v1
Revises: 0002_pg
Create Date: 2026-08-01 20:00:00.000000

Esta revision foi aplicada diretamente no banco durante desenvolvimento.
O arquivo é criado aqui apenas para que o Alembic reconheça a revisão
e o `upgrade head` não falhe com 'Can't locate revision identified by 0003_v1'.
"""
from typing import Sequence, Union

revision: str = "0003_v1"
down_revision: Union[str, None] = "0002_pg"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op: schema já está aplicado no banco.
    pass


def downgrade() -> None:
    # No-op: nada a desfazer.
    pass
