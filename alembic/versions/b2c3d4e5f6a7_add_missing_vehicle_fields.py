"""add missing vehicle fields

Revision ID: b2c3d4e5f6a7
Revises: 9a8b7c6d5e4f
Create Date: 2025-11-25 20:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = '9a8b7c6d5e4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('vehicles', sa.Column('brand', sa.String(length=50), nullable=True))
    op.add_column('vehicles', sa.Column('model', sa.String(length=50), nullable=True))
    op.add_column('vehicles', sa.Column('color', sa.String(length=50), nullable=True))
    op.add_column('vehicles', sa.Column('is_frequent', sa.Boolean(), server_default='false', nullable=True))
    
    # Update existing records to have is_frequent = False
    op.execute("UPDATE vehicles SET is_frequent = false WHERE is_frequent IS NULL")


def downgrade() -> None:
    op.drop_column('vehicles', 'is_frequent')
    op.drop_column('vehicles', 'color')
    op.drop_column('vehicles', 'model')
    op.drop_column('vehicles', 'brand')
