"""add_missing_columns_to_shifts

Revision ID: 86a8e86f8bf0
Revises: 8895265905aa
Create Date: 2025-11-22 12:13:36.352262

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '86a8e86f8bf0'
down_revision: Union[str, None] = '8895265905aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Aplicar los cambios a la base de datos (migración hacia adelante).
    """
    # Renombrar la columna con error de tipeo
    op.alter_column('shifts', 'tota_expenses', new_column_name='total_expenses')
    
    # Agregar las columnas faltantes
    op.add_column('shifts', sa.Column('initial_cash', sa.Integer(), server_default='0', nullable=True))
    op.add_column('shifts', sa.Column('final_cash', sa.Integer(), nullable=True))
    op.add_column('shifts', sa.Column('notes', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """
    Revertir los cambios (rollback).
    """
    # Eliminar las columnas agregadas
    op.drop_column('shifts', 'notes')
    op.drop_column('shifts', 'final_cash')
    op.drop_column('shifts', 'initial_cash')
    
    # Revertir el nombre de la columna
    op.alter_column('shifts', 'total_expenses', new_column_name='tota_expenses')
