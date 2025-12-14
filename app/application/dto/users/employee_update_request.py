from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional

class EmployeeUpdateRequest(BaseModel):
    """Request para actualizar un empleado existente."""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None
    commission_percentage: Optional[int] = None  # Solo para washers
    
    @field_validator('commission_percentage')
    @classmethod
    def validate_commission(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError('Commission percentage must be between 0 and 100')
        return v
