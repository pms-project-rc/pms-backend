from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.notifications.entities.notification import Notification

class INotificationRepository(ABC):
    @abstractmethod
    async def create(self, notification: Notification) -> Notification:
        pass

    @abstractmethod
    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        pass

    @abstractmethod
    async def mark_as_read(self, notification_id: int) -> Notification:
        pass

    @abstractmethod
    async def list_by_recipient(
        self, 
        recipient_type: str, 
        recipient_id: int, 
        unread_only: bool = False
    ) -> List[Notification]:
        pass

    @abstractmethod
    async def delete(self, notification_id: int):
        pass

    @abstractmethod
    async def count_unread(self, recipient_type: str, recipient_id: int) -> int:
        pass
