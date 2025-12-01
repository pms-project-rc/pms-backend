from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Rate:
    id: Optional[int]
    vehicle_type: str
    rate_type: str
    price: int
    description: Optional[str] = None
    is_active: bool = True
