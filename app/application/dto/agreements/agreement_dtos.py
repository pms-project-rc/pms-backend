from pydantic import BaseModel
from typing import Optional
from datetime import date

class AgreementRequest(BaseModel):
    company_name: str
    contact_name: str
    start_date: date
    discount_percentage: int
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    end_date: Optional[date] = None
    special_rate: Optional[int] = None
    notes: Optional[str] = None

class AgreementResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    contact_phone: Optional[str]
    contact_email: Optional[str]
    start_date: date
    end_date: Optional[date]
    discount_percentage: int
    special_rate: Optional[int]
    is_active: str
    notes: Optional[str]
    
    class Config:
        from_attributes = True

class AddVehicleRequest(BaseModel):
    plate: str
