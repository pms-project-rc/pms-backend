from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    status: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True
