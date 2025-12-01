from pydantic import BaseModel
from typing import Optional

class EntryRequest(BaseModel):
    plate: str
    vehicle_type: str
    owner_name: str
    owner_phone: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None
    helmet_count: int = 0
