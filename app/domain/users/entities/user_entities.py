"""
Entidades de dominio para el módulo de usuarios.

Estas entidades representan los conceptos de negocio fundamentales
y encapsulan la lógica de dominio relacionada con usuarios.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(Enum):
    """Enum para definir los tipos de roles de usuario en el sistema."""
    GLOBAL_ADMIN = "global_admin"
    OPERATIONAL_ADMIN = "operational_admin"
    WASHER = "washer"


@dataclass
class GlobalAdmin:
    """
    Entidad de dominio para Administradores Globales.
    
    Los Global Admins tienen control completo sobre el sistema,
    incluyendo configuración, gestión de usuarios y acceso a todos los reportes.
    """
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones básicas de la entidad."""
        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Email inválido: {self.email}")
        if self.full_name and len(self.full_name) < 3:
            raise ValueError("El nombre completo debe tener al menos 3 caracteres")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validación simple de email."""
        return "@" in email and "." in email.split("@")[1]
    
    def deactivate(self) -> None:
        """Desactiva al administrador global."""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Activa al administrador global."""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def record_login(self) -> None:
        """Registra el último inicio de sesión."""
        self.last_login = datetime.now()
        self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"<GlobalAdmin(id={self.id}, email='{self.email}', active={self.is_active})>"


@dataclass
class OperationalAdmin:
    """
    Entidad de dominio para Administradores Operacionales.
    
    Los Operational Admins gestionan las operaciones diarias del parqueadero,
    incluyendo entrada/salida de vehículos, servicios de lavado y turnos.
    """
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    phone: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones básicas de la entidad."""
        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Email inválido: {self.email}")
        if self.full_name and len(self.full_name) < 3:
            raise ValueError("El nombre completo debe tener al menos 3 caracteres")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validación simple de email."""
        return "@" in email and "." in email.split("@")[1]
    
    def deactivate(self) -> None:
        """Desactiva al administrador operacional."""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Activa al administrador operacional."""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def record_login(self) -> None:
        """Registra el último inicio de sesión."""
        self.last_login = datetime.now()
        self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"<OperationalAdmin(id={self.id}, email='{self.email}', active={self.is_active})>"


@dataclass
class Washer:
    """
    Entidad de dominio para Lavadores.
    
    Los Washers realizan servicios de lavado de vehículos y reciben
    bonos basados en su porcentaje de comisión.
    """
    id: Optional[int] = None
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    phone: Optional[str] = None
    commission_percentage: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    def __post_init__(self):
        """Validaciones de la entidad."""
        if self.email and not self._is_valid_email(self.email):
            raise ValueError(f"Email inválido: {self.email}")
        if self.full_name and len(self.full_name) < 3:
            raise ValueError("El nombre completo debe tener al menos 3 caracteres")
        if not (0 <= self.commission_percentage <= 100):
            raise ValueError(f"El porcentaje de comisión debe estar entre 0 y 100, recibido: {self.commission_percentage}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Validación simple de email."""
        return "@" in email and "." in email.split("@")[1]
    
    def set_commission_percentage(self, percentage: int) -> None:
        """
        Establece el porcentaje de comisión del lavador.
        
        Args:
            percentage: Porcentaje de comisión (0-100)
            
        Raises:
            ValueError: Si el porcentaje está fuera del rango válido
        """
        if not (0 <= percentage <= 100):
            raise ValueError(f"El porcentaje de comisión debe estar entre 0 y 100, recibido: {percentage}")
        self.commission_percentage = percentage
        self.updated_at = datetime.now()
    
    def calculate_bonus(self, service_price: float) -> float:
        """
        Calcula el bono del lavador basado en el precio del servicio.
        
        Args:
            service_price: Precio total del servicio de lavado
            
        Returns:
            El monto del bono a recibir
        """
        return service_price * (self.commission_percentage / 100)
    
    def deactivate(self) -> None:
        """Desactiva al lavador."""
        self.is_active = False
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Activa al lavador."""
        self.is_active = True
        self.updated_at = datetime.now()
    
    def record_login(self) -> None:
        """Registra el último inicio de sesión."""
        self.last_login = datetime.now()
        self.updated_at = datetime.now()
    
    def __repr__(self) -> str:
        return f"<Washer(id={self.id}, email='{self.email}', commission={self.commission_percentage}%, active={self.is_active})>"
