"""
Modelos SQLAlchemy para usuarios del sistema.
"""
from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from . import Base


class GlobalAdmin(Base):
    """Modelo para administradores globales del sistema."""
    
    __tablename__ = "global_admins"
    
    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relaciones
    business_configs = relationship("BusinessConfig", back_populates="admin")
    financial_reports = relationship("FinancialReport", back_populates="admin")
    
    def __repr__(self):
        return f"<GlobalAdmin(id={self.id}, email='{self.email}')>"


class OperationalAdmin(Base):
    """Modelo para administradores operacionales del parqueadero."""
    
    __tablename__ = "operational_admins"
    
    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relaciones
    shifts = relationship("Shift", back_populates="admin", cascade="all, delete-orphan")
    washing_services = relationship("WashingService", back_populates="admin")
    parking_records = relationship("ParkingRecord", back_populates="admin")
    
    def __repr__(self):
        return f"<OperationalAdmin(id={self.id}, email='{self.email}')>"


class Washer(Base):
    """Modelo para lavadores del parqueadero."""
    
    __tablename__ = "washers"
    
    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    commission_percentage = Column(Integer, default=0)  # 0-100
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    
    # Relaciones
    washing_services = relationship("WashingService", back_populates="washer", cascade="all, delete-orphan")
    bonuses = relationship("Bonus", back_populates="washer", cascade="all, delete-orphan")
    advances = relationship("EmployeeAdvance", back_populates="washer", cascade="all, delete-orphan")
    shifts = relationship("Shift", back_populates="washer", cascade="all, delete-orphan")
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            'commission_percentage >= 0 AND commission_percentage <= 100', 
            name='check_washers_commission_valid'
        ),
    )
    
    def __repr__(self):
        return f"<Washer(id={self.id}, email='{self.email}', name='{self.full_name}')>"

