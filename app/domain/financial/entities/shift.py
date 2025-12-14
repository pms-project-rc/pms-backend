from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Shift:
    shift_date: date
    start_time: datetime
    initial_cash: int = 0
    id: Optional[int] = None
    admin_id: Optional[int] = None
    washer_id: Optional[int] = None
    end_time: Optional[datetime] = None
    final_cash: Optional[int] = None
    total_income: int = 0
    total_expenses: int = 0
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
