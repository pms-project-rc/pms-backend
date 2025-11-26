"""add parking_rate_id to parking_records

Revision ID: d3e4f5g6h7i8
Revises: b2c3d4e5f6a7
Create Date: 2025-11-25 21:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3e4f5g6h7i8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('parking_records', sa.Column('parking_rate_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'parking_records', 'rates', ['parking_rate_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    op.drop_constraint(None, 'parking_records', type_='foreignkey')
    op.drop_column('parking_records', 'parking_rate_id')
