from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class MonthlySubscription:
    id: Optional[int]
    vehicle_id: int
    start_date: date
    end_date: date
    monthly_fee: int
    payment_status: str = "pending"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
