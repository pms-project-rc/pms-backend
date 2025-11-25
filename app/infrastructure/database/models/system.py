"""
Modelos SQLAlchemy para configuración del sistema, auditoría y notificaciones.
"""
from sqlalchemy import TIMESTAMP, Boolean, CheckConstraint, Column, Index, Integer, String, Text
from sqlalchemy.sql import func

from . import Base


class BusinessConfig(Base):
    """Modelo para configuración del negocio."""

    __tablename__ = "business_config"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True)
    config_value = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    data_type = Column(String(20), default="string")  # string, integer, boolean, json
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "data_type IN ('string', 'integer', 'boolean', 'json')",
            name='check_business_config_data_type_valid'
        ),
    )

    def __repr__(self):
        return f"<BusinessConfig(key='{self.config_key}', value='{self.config_value}')>"


class AuditLog(Base):
    """Modelo para auditoría de acciones del sistema."""

    __tablename__ = "audit_logs"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String(50), nullable=False, index=True)  # global_admin, operational_admin, washer
    user_id = Column(Integer, nullable=False, index=True)
    action = Column(String(100), nullable=False, index=True)  # create, update, delete, login, logout
    entity_type = Column(String(50), nullable=True)  # vehicle, parking_record, washing_service
    entity_id = Column(Integer, nullable=True)
    details = Column(Text, nullable=True)  # JSON con detalles de la acción
    ip_address = Column(String(50), nullable=True)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Índices
    __table_args__ = (
        Index('ix_audit_logs_user', 'user_type', 'user_id'),
        Index('ix_audit_logs_entity', 'entity_type', 'entity_id'),
        Index('ix_audit_logs_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user='{self.user_type}:{self.user_id}', action='{self.action}')>"


class Notification(Base):
    """Modelo para notificaciones del sistema."""

    __tablename__ = "notifications"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    recipient_type = Column(String(50), nullable=False, index=True)  # global_admin, operational_admin, washer
    recipient_id = Column(Integer, nullable=False, index=True)
    notification_type = Column(String(50), nullable=False, index=True)  # alert, warning, info, success
    title = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False, index=True)
    read_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False, index=True)

    # Índices
    __table_args__ = (
        Index('ix_notifications_recipient', 'recipient_type', 'recipient_id'),
        Index('ix_notifications_is_read', 'is_read'),
        CheckConstraint(
            "notification_type IN ('alert', 'warning', 'info', 'success')",
            name='check_notifications_type_valid'
        ),
    )

    def __repr__(self):
        return f"<Notification(id={self.id}, to='{self.recipient_type}:{self.recipient_id}', read={self.is_read})>"


class FinancialReport(Base):
    """Modelo para reportes financieros pre-calculados."""

    __tablename__ = "financial_reports"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    report_type = Column(String(50), nullable=False, index=True)  # daily, weekly, monthly, yearly
    report_date = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    total_income = Column(Integer, default=0)  # En centavos
    total_expenses = Column(Integer, default=0)  # En centavos
    net_profit = Column(Integer, default=0)  # En centavos
    parking_count = Column(Integer, default=0)
    washing_count = Column(Integer, default=0)
    subscription_count = Column(Integer, default=0)
    report_data = Column(Text, nullable=True)  # JSON con detalles adicionales
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Índices
    __table_args__ = (
        Index('ix_financial_reports_type_date', 'report_type', 'report_date'),
        CheckConstraint(
            "report_type IN ('daily', 'weekly', 'monthly', 'yearly')",
            name='check_financial_reports_type_valid'
        ),
    )

    def __repr__(self):
        return f"<FinancialReport(id={self.id}, type='{self.report_type}', date={self.report_date})>"


class PasswordResetToken(Base):
    """Modelo para tokens de recuperación de contraseña."""

    __tablename__ = "password_reset_tokens"

    # Columnas
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String(50), nullable=False, index=True)  # global_admin, operational_admin, washer
    user_id = Column(Integer, nullable=False, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False, index=True)
    is_used = Column(Boolean, default=False, index=True)
    used_at = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Índices
    __table_args__ = (
        Index('ix_password_reset_tokens_user', 'user_type', 'user_id'),
        Index('ix_password_reset_tokens_token_valid', 'token', 'is_used', 'expires_at'),
    )

    def __repr__(self):
        return f"<PasswordResetToken(id={self.id}, user='{self.user_type}:{self.user_id}', used={self.is_used})>"
