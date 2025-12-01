from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ParkingRecordResponse(BaseModel):
    id: int
    vehicle_id: int
    plate: str
    vehicle_type: str
    owner_name: str
    entry_time: datetime
    exit_time: Optional[datetime] = None
    helmet_count: int
    helmet_charge: int
    total_cost: int
    payment_status: str
    duration_hours: Optional[float] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class VehicleResponse(BaseModel):
    id: int
    plate: str
    vehicle_type: str
    owner_name: str
    owner_phone: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    is_frequent: bool
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True


class ActiveParkingResponse(BaseModel):
    id: int
    vehicle_id: int
    plate: str
    vehicle_type: str
    owner_name: str
    entry_time: datetime
    helmet_count: int
    helmet_charge: int
    notes: Optional[str] = None
    duration_so_far: str  # Human readable duration like "2h 30m"
    
    class Config:
        from_attributes = True
