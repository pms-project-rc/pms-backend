"""
Modelos SQLAlchemy para servicios de lavado y tarifas.
"""
from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    CheckConstraint,
    Column,
    ForeignKey,
    Index,
    Integer,
    String,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from . import Base


class Rate(Base):
    """Modelo para tarifas de parqueo."""

    __tablename__ = "rates"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(String(50), nullable=False, index=True)  # Moto, Carro, etc.
    rate_type = Column(String(50), nullable=False, index=True)  # Hora, Día, Noche, Mes
    price = Column(Integer, nullable=False)  # En centavos
    description = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    parking_records = relationship("ParkingRecord", back_populates="rate")

    # Constraints
    __table_args__ = (
        Index('ix_rates_vehicle_type_rate_type', 'vehicle_type', 'rate_type'),
        CheckConstraint('price >= 0', name='check_rates_price_positive'),
    )

    def __repr__(self):
        return f"<Rate(id={self.id}, type='{self.vehicle_type}', rate='{self.rate_type}', price={self.price})>"


class WashingService(Base):
    """Modelo para servicios de lavado."""

    __tablename__ = "washing_services"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    parking_record_id = Column(
        Integer, ForeignKey("parking_records.id", ondelete="CASCADE"), nullable=True, unique=True
    )
    washer_id = Column(Integer, ForeignKey("washers.id", ondelete="RESTRICT"), nullable=True)
    service_type = Column(String(50), nullable=False)  # Básico, Completo, Premium
    service_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    price = Column(Integer, nullable=False)  # En centavos
    payment_status = Column(String(20), default="pending")  # pending, paid, cancelled
    notes = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    vehicle = relationship("Vehicle", back_populates="washing_services")
    parking_record = relationship("ParkingRecord", back_populates="washing_service")
    washer = relationship("Washer", back_populates="washing_services")

    # Constraints
    __table_args__ = (
        Index('ix_washing_services_service_date', 'service_date'),
        Index('ix_washing_services_payment_status', 'payment_status'),
        CheckConstraint('price >= 0', name='check_washing_services_price_positive'),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'cancelled')",
            name='check_washing_services_payment_status_valid'
        ),
    )

    def __repr__(self):
        return f"<WashingService(id={self.id}, type='{self.service_type}', price={self.price})>"
