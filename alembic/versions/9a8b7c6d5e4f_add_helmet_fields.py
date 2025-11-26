"""add helmet fields

Revision ID: 9a8b7c6d5e4f
Revises: 8895265905aa
Create Date: 2025-11-25 20:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a8b7c6d5e4f'
down_revision: Union[str, None] = '8895265905aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('parking_records', sa.Column('helmet_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('parking_records', sa.Column('helmet_charge', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('parking_records', 'helmet_charge')
    op.drop_column('parking_records', 'helmet_count')
