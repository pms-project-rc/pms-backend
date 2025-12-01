from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional

@dataclass
class Agreement:
    id: Optional[int]
    company_name: str
    contact_name: str
    start_date: date
    discount_percentage: int
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    end_date: Optional[date] = None
    special_rate: Optional[int] = None
    is_active: str = "active"
    notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
