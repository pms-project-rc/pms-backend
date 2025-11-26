"""
Modelos SQLAlchemy para vehículos y registros de parqueo.
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


class Vehicle(Base):
    """Modelo para vehículos registrados en el sistema."""

    __tablename__ = "vehicles"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    plate = Column(String(20), unique=True, nullable=False, index=True)
    owner_name = Column(String(100), nullable=False)
    owner_phone = Column(String(20), nullable=True)
    vehicle_type = Column(Enum(VehicleType, name='vehicle_type', values_callable=lambda x: [e.value for e in x]), nullable=False)  # Moto, Carro, etc.
    brand = Column(String(50), nullable=True)
    model = Column(String(50), nullable=True)
    color = Column(String(50), nullable=True)
    is_frequent = Column(Boolean, default=False)
    notes = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    parking_records = relationship("ParkingRecord", back_populates="vehicle", cascade="all, delete-orphan")
    washing_services = relationship("WashingService", back_populates="vehicle", cascade="all, delete-orphan")
    agreement_vehicles = relationship("AgreementVehicle", back_populates="vehicle", cascade="all, delete-orphan")

    # Índices adicionales
    __table_args__ = (
        Index('ix_vehicles_owner_name', 'owner_name'),
        Index('ix_vehicles_vehicle_type', 'vehicle_type'),
        Index('ix_vehicles_is_frequent', 'is_frequent'),
    )

    def __repr__(self):
        return f"<Vehicle(id={self.id}, plate='{self.plate}', type='{self.vehicle_type}')>"


class ParkingRecord(Base):
    """Modelo para registros de parqueo (entradas y salidas)."""

    __tablename__ = "parking_records"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    entry_time = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    exit_time = Column(TIMESTAMP(timezone=True), nullable=True)
    parking_rate_id = Column(Integer, ForeignKey("rates.id", ondelete="RESTRICT"), nullable=False)
    monthly_subscription_id = Column(Integer, ForeignKey("monthly_subscriptions.id", ondelete="SET NULL"), nullable=True)
    washing_service_id = Column(Integer, ForeignKey("washing_services.id", ondelete="SET NULL"), nullable=True)
    helmet_count = Column(Integer, default=0, nullable=False)  # Number of helmets (motorcycles only)
    helmet_charge = Column(Integer, default=0, nullable=False)  # Helmet charge in cents
    total_cost = Column(Integer, default=0)  # En centavos
    payment_status = Column(String(20), default="pending")  # pending, paid, cancelled
    notes = Column(String(255), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relaciones
    vehicle = relationship("Vehicle", back_populates="parking_records")
    rate = relationship("Rate", back_populates="parking_records")
    subscription = relationship("MonthlySubscription", back_populates="parking_records")
    washing_service = relationship("WashingService", back_populates="parking_record", uselist=False, foreign_keys="[WashingService.parking_record_id]")

    # Constraints
    __table_args__ = (
        Index('ix_parking_records_entry_time', 'entry_time'),
        Index('ix_parking_records_exit_time', 'exit_time'),
        Index('ix_parking_records_payment_status', 'payment_status'),
        CheckConstraint('total_cost >= 0', name='check_parking_records_total_cost_positive'),
        CheckConstraint(
            "payment_status IN ('pending', 'paid', 'cancelled')",
            name='check_parking_records_payment_status_valid'
        ),
    )

    def __repr__(self):
        return f"<ParkingRecord(id={self.id}, vehicle_id={self.vehicle_id}, status='{self.payment_status}')>"
