from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = None
    role: str = Field(..., description="admin/washer/customer")

class UserUpdateRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
