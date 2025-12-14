"""Add washer_id to shifts table for washer shift management.

Revision ID: add_washer_shifts
Revises: 68e02f84ead7
Create Date: 2025-12-09

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_washer_shifts'
down_revision = '68e02f84ead7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add washer_id column
    op.add_column('shifts', sa.Column('washer_id', sa.Integer(), nullable=True))
    
    # Add foreign key constraint
    op.create_foreign_key(
        'fk_shifts_washer_id',
        'shifts', 'washers',
        ['washer_id'], ['id'],
        ondelete='RESTRICT'
    )
    
    # Add index on washer_id
    op.create_index('ix_shifts_washer_id', 'shifts', ['washer_id'])
    
    # Make admin_id nullable (since shifts can now be for admins OR washers)
    op.alter_column('shifts', 'admin_id', existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    # Revert admin_id to non-nullable
    op.alter_column('shifts', 'admin_id', existing_type=sa.Integer(), nullable=False)
    
    # Drop index
    op.drop_index('ix_shifts_washer_id', table_name='shifts')
    
    # Drop foreign key
    op.drop_constraint('fk_shifts_washer_id', 'shifts', type_='foreignkey')
    
    # Drop column
    op.drop_column('shifts', 'washer_id')
