from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class ParkingRecord:
    id: Optional[int]
    vehicle_id: int
    shift_id: int
    admin_id: int
    entry_time: datetime
    parking_rate_id: int
    exit_time: Optional[datetime] = None
    subscription_id: Optional[int] = None
    washing_service_id: Optional[int] = None
    helmet_count: int = 0
    helmet_charge: int = 0
    total_cost: int = 0
    payment_status: str = "pending"
    notes: Optional[str] = None
