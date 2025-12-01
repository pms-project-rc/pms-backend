from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    recipient_type: str
    recipient_id: int
    notification_type: str
    title: str
    message: str
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationCreateRequest(BaseModel):
    title: str
    message: str
    notification_type: str = "info"
