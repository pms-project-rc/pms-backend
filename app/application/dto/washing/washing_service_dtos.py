from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class WashingServiceRequest(BaseModel):
    plate: str
    vehicle_type: str
    service_type: str
    price: int
    owner_name: str
    owner_phone: Optional[str] = None
    washer_id: Optional[int] = None
    notes: Optional[str] = None

class WashingServiceResponse(BaseModel):
    id: int
    vehicle_id: int
    plate: str
    service_type: str
    price: int
    status: str
    washer_id: Optional[int] = None
    service_date: datetime
    
    class Config:
        from_attributes = True
