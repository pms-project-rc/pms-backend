from pydantic import BaseModel
from typing import Optional
from datetime import date

class SubscriptionRequest(BaseModel):
    plate: str
    vehicle_type: str
    owner_name: str
    owner_phone: str
    monthly_fee: int
    start_date: date
    duration_days: int = 30
    notes: Optional[str] = None

class SubscriptionResponse(BaseModel):
    id: int
    vehicle_id: int
    plate: str
    start_date: date
    end_date: date
    monthly_fee: int
    payment_status: str
    days_remaining: int
    
    class Config:
        from_attributes = True
