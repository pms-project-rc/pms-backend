from pydantic import BaseModel
from typing import Optional

class ExitRequest(BaseModel):
    plate: str
    notes: Optional[str] = None
