from abc import ABC, abstractmethod
from typing import Optional
from app.domain.users.entities.operational_admin import OperationalAdmin

class IOperationalAdminRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[OperationalAdmin]:
        pass

    @abstractmethod
    async def get_by_id(self, admin_id: int) -> Optional[OperationalAdmin]:
        pass

    @abstractmethod
    async def create(self, admin: OperationalAdmin) -> OperationalAdmin:
        pass

    @abstractmethod
    async def update_last_login(self, admin_id: int):
        pass
