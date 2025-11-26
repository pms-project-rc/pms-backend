from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserCreateRequest(BaseModel):
    full_name: str = Field(..., min_length=2)
    email: EmailStr
    phone: Optional[str] = None
    status: Optional[str] = "active"

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None
