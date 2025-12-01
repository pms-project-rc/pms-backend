from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class WashingService:
    id: Optional[int]
    vehicle_id: int
    shift_id: int
    admin_id: int
    service_type: str
    service_date: datetime
    price: int
    parking_record_id: Optional[int] = None
    washer_id: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    payment_status: str = "pending"
    notes: Optional[str] = None
