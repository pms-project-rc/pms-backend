"""
Pydantic schemas (DTOs) para el módulo de usuarios.

Estos schemas definen la estructura de datos para requests y responses
de la API REST.
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime


# ========== Request Schemas (Input) ==========

class CreateGlobalAdminRequest(BaseModel):
    """Schema para crear un Global Admin."""
    email: EmailStr = Field(..., description="Email del administrador")
    password: str = Field(..., min_length=8, description="Contraseña (mínimo 8 caracteres)")
    full_name: str = Field(..., min_length=3, max_length=100, description="Nombre completo")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono (opcional)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "admin@pms.com",
                "password": "SecurePass123!",
                "full_name": "Juan Pérez González",
                "phone": "+573001234567"
            }
        }
    )


class UpdateGlobalAdminRequest(BaseModel):
    """Schema para actualizar un Global Admin."""
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Juan Pérez González",
                "phone": "+573001234567",
                "is_active": True
            }
        }
    )


class CreateOperationalAdminRequest(BaseModel):
    """Schema para crear un Operational Admin."""
    email: EmailStr = Field(..., description="Email del administrador")
    password: str = Field(..., min_length=8, description="Contraseña")
    full_name: str = Field(..., min_length=3, max_length=100, description="Nombre completo")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono (opcional)")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "operador@pms.com",
                "password": "SecurePass123!",
                "full_name": "María López",
                "phone": "+573007654321"
            }
        }
    )


class UpdateOperationalAdminRequest(BaseModel):
    """Schema para actualizar un Operational Admin."""
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None


class CreateWasherRequest(BaseModel):
    """Schema para crear un Washer."""
    email: EmailStr = Field(..., description="Email del lavador")
    password: str = Field(..., min_length=8, description="Contraseña")
    full_name: str = Field(..., min_length=3, max_length=100, description="Nombre completo")
    phone: Optional[str] = Field(None, max_length=20, description="Teléfono (opcional)")
    commission_percentage: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Porcentaje de comisión (0-100)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "lavador@pms.com",
                "password": "SecurePass123!",
                "full_name": "Carlos Ramírez",
                "phone": "+573009876543",
                "commission_percentage": 15
            }
        }
    )


class UpdateWasherRequest(BaseModel):
    """Schema para actualizar un Washer."""
    full_name: Optional[str] = Field(None, min_length=3, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    commission_percentage: Optional[int] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "full_name": "Carlos Ramírez Díaz",
                "commission_percentage": 20,
                "is_active": True
            }
        }
    )


# ========== Response Schemas (Output) ==========

class UserBaseResponse(BaseModel):
    """Schema base para respuestas de usuarios."""
    id: int
    email: str
    full_name: str
    phone: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


class GlobalAdminResponse(UserBaseResponse):
    """Schema de respuesta para Global Admin."""
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "email": "admin@pms.com",
                "full_name": "Juan Pérez González",
                "phone": "+573001234567",
                "is_active": True,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00",
                "last_login": "2024-01-15T08:30:00"
            }
        }
    )


class OperationalAdminResponse(UserBaseResponse):
    """Schema de respuesta para Operational Admin."""
    
    model_config = ConfigDict(from_attributes=True)


class WasherResponse(UserBaseResponse):
    """Schema de respuesta para Washer."""
    commission_percentage: int = Field(..., description="Porcentaje de comisión")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 3,
                "email": "lavador@pms.com",
                "full_name": "Carlos Ramírez",
                "phone": "+573009876543",
                "commission_percentage": 15,
                "is_active": True,
                "created_at": "2024-01-01T10:00:00",
                "updated_at": "2024-01-01T10:00:00",
                "last_login": None
            }
        }
    )


class UserListResponse(BaseModel):
    """Schema de respuesta para listas de usuarios."""
    total: int = Field(..., description="Total de usuarios")
    users: list[UserBaseResponse] = Field(..., description="Lista de usuarios")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total": 2,
                "users": [
                    {
                        "id": 1,
                        "email": "admin@pms.com",
                        "full_name": "Juan Pérez",
                        "phone": None,
                        "is_active": True,
                        "created_at": "2024-01-01T10:00:00",
                        "updated_at": "2024-01-01T10:00:00",
                        "last_login": None
                    }
                ]
            }
        }
    )


class MessageResponse(BaseModel):
    """Schema genérico para mensajes de respuesta."""
    message: str = Field(..., description="Mensaje de respuesta")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Usuario eliminado exitosamente"
            }
        }
    )
