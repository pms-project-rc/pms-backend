"""
Modelos SQLAlchemy para gestión financiera (turnos, gastos, bonos, vouchers).
"""
from sqlalchemy import TIMESTAMP, CheckConstraint, Column, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class Shift(Base):
    """Modelo para turnos de trabajo."""

    __tablename__ = "shifts"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("operational_admins.id", ondelete="RESTRICT"), nullable=False, index=True)
    shift_date = Column(Date, nullable=False, index=True)
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=True)
    initial_cash = Column(Integer, default=0)  # En centavos
    final_cash = Column(Integer, nullable=True)  # En centavos
    total_income = Column(Integer, default=0)  # En centavos
    total_expenses = Column(Integer, default=0)  # En centavos
    notes = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    admin = relationship("OperationalAdmin", back_populates="shifts")
    expenses = relationship("Expense", back_populates="shift", cascade="all, delete-orphan")
    bonuses = relationship("Bonus", back_populates="shift", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        Index('ix_shifts_shift_date', 'shift_date'),
        Index('ix_shifts_admin_date', 'admin_id', 'shift_date'),
        CheckConstraint('initial_cash >= 0', name='check_shifts_initial_cash_positive'),
        CheckConstraint('final_cash >= 0', name='check_shifts_final_cash_positive'),
        CheckConstraint('total_income >= 0', name='check_shifts_total_income_positive'),
        CheckConstraint('total_expenses >= 0', name='check_shifts_total_expenses_positive'),
    )

    def __repr__(self):
        return f"<Shift(id={self.id}, admin_id={self.admin_id}, date={self.shift_date})>"


class Expense(Base):
    """Modelo para gastos del parqueadero."""

    __tablename__ = "expenses"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=True, index=True)
    expense_type = Column(String(50), nullable=False, index=True)  # Mantenimiento, Servicios, Otros
    amount = Column(Integer, nullable=False)  # En centavos
    description = Column(String(255), nullable=False)
    expense_date = Column(Date, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    shift = relationship("Shift", back_populates="expenses")

    # Constraints
    __table_args__ = (
        Index('ix_expenses_expense_date', 'expense_date'),
        Index('ix_expenses_expense_type', 'expense_type'),
        CheckConstraint('amount >= 0', name='check_expenses_amount_positive'),
    )

    def __repr__(self):
        return f"<Expense(id={self.id}, type='{self.expense_type}', amount={self.amount})>"


class Bonus(Base):
    """Modelo para bonificaciones a lavadores."""

    __tablename__ = "bonuses"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    washer_id = Column(Integer, ForeignKey("washers.id", ondelete="CASCADE"), nullable=False, index=True)
    shift_id = Column(Integer, ForeignKey("shifts.id", ondelete="CASCADE"), nullable=True, index=True)
    amount = Column(Integer, nullable=False)  # En centavos
    reason = Column(String(255), nullable=True)
    bonus_date = Column(Date, nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    washer = relationship("Washer", back_populates="bonuses")
    shift = relationship("Shift", back_populates="bonuses")

    # Constraints
    __table_args__ = (
        Index('ix_bonuses_bonus_date', 'bonus_date'),
        Index('ix_bonuses_washer_date', 'washer_id', 'bonus_date'),
        CheckConstraint('amount >= 0', name='check_bonuses_amount_positive'),
    )

    def __repr__(self):
        return f"<Bonus(id={self.id}, washer_id={self.washer_id}, amount={self.amount})>"


class Voucher(Base):
    """Modelo para vouchers de pago."""

    __tablename__ = "vouchers"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    voucher_number = Column(String(50), unique=True, nullable=False, index=True)
    entity = Column(String(100), nullable=False)  # Nequi, Bancolombia, etc.
    amount = Column(Integer, nullable=False)  # En centavos
    payment_date = Column(Date, nullable=False, index=True)
    reference_number = Column(String(100), nullable=True)
    notes = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        Index('ix_vouchers_payment_date', 'payment_date'),
        Index('ix_vouchers_entity', 'entity'),
        CheckConstraint('amount >= 0', name='check_vouchers_amount_positive'),
    )

    def __repr__(self):
        return f"<Voucher(id={self.id}, number='{self.voucher_number}', amount={self.amount})>"
