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
    Integer,
    String,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.domain.parking.value_objects.vehicle_type import VehicleType
from . import Base


class Rate(Base):
    """Modelo para tarifas de parqueo y lavado."""

    __tablename__ = "rates"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    vehicle_type = Column(Enum(VehicleType, name='vehicle_type', values_callable=lambda x: [e.value for e in x]), nullable=False, unique=True)
    parking_rate_per_minute = Column(Integer, nullable=True)  # En centavos
    parking_flat_rate = Column(Integer, nullable=True)  # En centavos
    
    # Tarifas de lavado
    wash_basico = Column(Integer, nullable=True)
    wash_especial = Column(Integer, nullable=True)
    wash_completo = Column(Integer, nullable=True)
    wash_lujo = Column(Integer, nullable=True)
    wash_moto = Column(Integer, nullable=True)
    
    # Minutos gratis
    basico_free_minutes = Column(Integer, default=0)
    especial_free_minutes = Column(Integer, default=0)
    completo_free_minutes = Column(Integer, default=0)
    lujo_free_minutes = Column(Integer, default=0)
    moto_free_minutes = Column(Integer, default=0)
    
    # Tarifas extra
    helmet_fee = Column(Integer, default=0)  # En centavos
    
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    parking_records = relationship("ParkingRecord", back_populates="rate")

    def __repr__(self):
        return f"<Rate(id={self.id}, type='{self.vehicle_type}')>"


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
    parking_record = relationship("ParkingRecord", back_populates="washing_service", foreign_keys=[parking_record_id])
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
