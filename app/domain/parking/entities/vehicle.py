from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Vehicle:
    id: Optional[int]
    plate: str
    vehicle_type: str
    owner_name: str
    owner_phone: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    is_frequent: bool = False
    notes: Optional[str] = None
