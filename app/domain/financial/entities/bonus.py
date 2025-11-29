from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Bonus:
    id: Optional[int]
    washer_id: int
    shift_id: Optional[int]
    amount: int
    reason: Optional[str]
    bonus_date: date
