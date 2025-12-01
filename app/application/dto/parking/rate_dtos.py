from pydantic import BaseModel
from typing import Optional

class RateRequest(BaseModel):
    vehicle_type: str
    rate_type: str
    price: int
    description: Optional[str] = None
    is_active: bool = True

class RateResponse(BaseModel):
    id: int
    vehicle_type: str
    rate_type: str
    price: int
    description: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True
