from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Notification:
    id: Optional[int]
    recipient_type: str
    recipient_id: int
    notification_type: str
    title: str
    message: str
    is_read: bool = False
    read_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
