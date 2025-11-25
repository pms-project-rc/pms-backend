"""
Modelos SQLAlchemy para suscripciones mensuales y convenios.
"""
from sqlalchemy import TIMESTAMP, CheckConstraint, Column, Date, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class MonthlySubscription(Base):
    """Modelo para suscripciones mensuales de parqueo."""

    __tablename__ = "monthly_subscriptions"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    start_date = Column(Date, nullable=False, index=True)
    end_date = Column(Date, nullable=False, index=True)
    monthly_fee = Column(Integer, nullable=False)  # En centavos
    payment_status = Column(String(20), default="pending")  # pending, paid, cancelled
    notes = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    vehicle = relationship("Vehicle")
    parking_records = relationship("ParkingRecord", back_populates="subscription")

    # Constraints
    __table_args__ = (
        Index('ix_monthly_subscriptions_dates', 'start_date', 'end_date'),
        Index('ix_monthly_subscriptions_payment_status', 'payment_status'),
        CheckConstraint('monthly_fee >= 0', name='check_monthly_subscriptions_fee_positive'),
        CheckConstraint('end_date >= start_date', name='check_monthly_subscriptions_dates_valid'),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'cancelled')",
            name='check_monthly_subscriptions_payment_status_valid'
        ),
    )

    def __repr__(self):
        return f"<MonthlySubscription(id={self.id}, vehicle_id={self.vehicle_id}, status='{self.payment_status}')>"


class Agreement(Base):
    """Modelo para convenios con empresas."""

    __tablename__ = "agreements"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    company_name = Column(String(100), nullable=False, index=True)
    contact_name = Column(String(100), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    discount_percentage = Column(Integer, default=0)  # 0-100
    special_rate = Column(Integer, nullable=True)  # En centavos (si aplica tarifa fija)
    is_active = Column(String(20), default="active")  # active, inactive, expired
    notes = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    agreement_vehicles = relationship("AgreementVehicle", back_populates="agreement", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        Index('ix_agreements_company_name', 'company_name'),
        Index('ix_agreements_is_active', 'is_active'),
        CheckConstraint(
            'discount_percentage >= 0 AND discount_percentage <= 100',
            name='check_agreements_discount_valid'
        ),
        CheckConstraint(
            "is_active IN ('active', 'inactive', 'expired')",
            name='check_agreements_is_active_valid'
        ),
    )

    def __repr__(self):
        return f"<Agreement(id={self.id}, company='{self.company_name}', status='{self.is_active}')>"


class AgreementVehicle(Base):
    """Modelo para vehículos asociados a convenios (tabla intermedia)."""

    __tablename__ = "agreement_vehicles"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    agreement_id = Column(Integer, ForeignKey("agreements.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    agreement = relationship("Agreement", back_populates="agreement_vehicles")
    vehicle = relationship("Vehicle", back_populates="agreement_vehicles")

    # Constraints
    __table_args__ = (
        Index('ix_agreement_vehicles_unique', 'agreement_id', 'vehicle_id', unique=True),
    )

    def __repr__(self):
        return f"<AgreementVehicle(agreement_id={self.agreement_id}, vehicle_id={self.vehicle_id})>"
