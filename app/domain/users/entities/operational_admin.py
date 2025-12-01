from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class OperationalAdmin:
    id: Optional[int]
    email: str
    full_name: str
    password_hash: str
    is_active: bool
    last_login: Optional[datetime] = None
    phone: Optional[str] = None
