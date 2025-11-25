"""
SQLAlchemy Base and Models

Este archivo contiene la definición de Base de SQLAlchemy
y todos los modelos de la base de datos.

IMPORTANTE: Todos los modelos deben importarse aquí para que
Alembic pueda detectarlos automáticamente.
"""

from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

# Convención de nombres para constraints (índices, foreign keys, etc.)
# Esto hace que Alembic genere nombres consistentes
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

metadata = MetaData(naming_convention=naming_convention)
Base = declarative_base(metadata=metadata)

# ============================================================================
# IMPORTAR TODOS LOS MODELOS AQUÍ
# ============================================================================
# IMPORTANTE: Todos los modelos DEBEN estar importados para que Alembic los detecte

# Modelos de Usuarios
# Modelos de Gestión Financiera
from app.infrastructure.database.models.financial import Bonus, Expense, Shift, Voucher

# Modelos de Servicios y Tarifas
from app.infrastructure.database.models.services import Rate, WashingService

# Modelos de Suscripciones y Convenios
from app.infrastructure.database.models.subscriptions import (
    Agreement,
    AgreementVehicle,
    MonthlySubscription,
)

# Modelos de Sistema y Configuración
from app.infrastructure.database.models.system import (
    AuditLog,
    BusinessConfig,
    FinancialReport,
    Notification,
    PasswordResetToken,
)
from app.infrastructure.database.models.users import GlobalAdmin, OperationalAdmin, Washer

# Modelos de Vehículos y Parqueo
from app.infrastructure.database.models.vehicles import ParkingRecord, Vehicle

__all__ = [
    # Base
    "Base",
    "metadata",

    # Usuarios
    "GlobalAdmin",
    "OperationalAdmin",
    "Washer",

    # Vehículos y Parqueo
    "Vehicle",
    "ParkingRecord",

    # Servicios y Tarifas
    "Rate",
    "WashingService",

    # Suscripciones y Convenios
    "MonthlySubscription",
    "Agreement",
    "AgreementVehicle",

    # Gestión Financiera
    "Shift",
    "Expense",
    "Bonus",
    "Voucher",

    # Sistema y Configuración
    "BusinessConfig",
    "AuditLog",
    "Notification",
    "FinancialReport",
    "PasswordResetToken",
]
