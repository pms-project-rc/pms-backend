from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class EmployeeResponse(BaseModel):
    """Respuesta unificada para cualquier tipo de empleado."""
    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str  # 'global_admin', 'operational_admin', 'washer'
    is_active: bool
    created_at: datetime
    commission_percentage: Optional[int] = None  # Solo para washers
    
    class Config:
        from_attributes = True
