from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class EmployeeCreateRequest(BaseModel):
    """Request para crear un nuevo empleado."""
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    role: str  # 'global_admin', 'operational_admin', 'washer'
    commission_percentage: Optional[int] = 0  # Solo para washers
    
    @field_validator('role')
    @classmethod
    def validate_role(cls, v):
        valid_roles = ['global_admin', 'operational_admin', 'washer']
        if v not in valid_roles:
            raise ValueError(f'Role must be one of {valid_roles}')
        return v
    
    @field_validator('commission_percentage')
    @classmethod
    def validate_commission(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Commission percentage must be between 0 and 100')
        return v
