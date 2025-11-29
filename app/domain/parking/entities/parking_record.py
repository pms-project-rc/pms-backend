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
    exit_time: Optional[datetime]
    parking_rate_id: int
    subscription_id: Optional[int]
    washing_service_id: Optional[int]
    helmet_count: int
    helmet_charge: int
    total_cost: int
    payment_status: str
    notes: Optional[str]
