"""
Modelos SQLAlchemy para gestión financiera (turnos, gastos, bonos, vouchers).
"""
from sqlalchemy import Column, Integer, String, Date, ForeignKey, TIMESTAMP, Index, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base


class Shift(Base):
    """Modelo para turnos de trabajo."""
    
    __tablename__ = "shifts"
    
    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, ForeignKey("operational_admins.id", ondelete="RESTRICT"), nullable=True, index=True)
    washer_id = Column(Integer, ForeignKey("washers.id", ondelete="RESTRICT"), nullable=True, index=True)
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
    washer = relationship("Washer", back_populates="shifts")
    expenses = relationship("Expense", back_populates="shift", cascade="all, delete-orphan")
    bonuses = relationship("Bonus", back_populates="shift", cascade="all, delete-orphan")
    washing_services = relationship("WashingService", back_populates="shift")
    parking_records = relationship("ParkingRecord", back_populates="shift")
    financial_reports = relationship("FinancialReport", back_populates="shift")
    
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
        owner = f"admin_id={self.admin_id}" if self.admin_id else f"washer_id={self.washer_id}"
        return f"<Shift(id={self.id}, {owner}, date={self.shift_date})>"


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


class EmployeeAdvance(Base):
    """Modelo para vales/préstamos a empleados."""
    
    __tablename__ = "employee_advances"
    
    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    washer_id = Column(Integer, ForeignKey("washers.id", ondelete="RESTRICT"), nullable=False, index=True)
    total_amount = Column(Integer, nullable=False)  # En centavos
    number_of_installments = Column(Integer, nullable=False)
    installment_amount = Column(Integer, nullable=False)  # En centavos
    remaining_amount = Column(Integer, nullable=False)  # En centavos
    status = Column(String(20), default="active", index=True)  # active, paid, cancelled
    description = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relaciones
    washer = relationship("Washer", back_populates="advances")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('total_amount > 0', name='check_advances_total_amount_positive'),
        CheckConstraint('number_of_installments > 0', name='check_advances_installments_positive'),
        CheckConstraint('installment_amount > 0', name='check_advances_installment_amount_positive'),
        CheckConstraint("status IN ('active', 'paid', 'cancelled')", name='check_advances_status_valid'),
    )
    
    def __repr__(self):
        return f"<EmployeeAdvance(id={self.id}, washer_id={self.washer_id}, remaining={self.remaining_amount})>"
