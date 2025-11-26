"""add cost fields to parking_records

Revision ID: e4f5g6h7i8j9
Revises: d3e4f5g6h7i8
Create Date: 2025-11-25 21:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f5g6h7i8j9'
down_revision: Union[str, None] = 'd3e4f5g6h7i8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('parking_records', sa.Column('total_cost', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('parking_records', sa.Column('payment_status', sa.String(length=20), nullable=True, server_default='pending'))
    op.add_column('parking_records', sa.Column('notes', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('parking_records', 'notes')
    op.drop_column('parking_records', 'payment_status')
    op.drop_column('parking_records', 'total_cost')
