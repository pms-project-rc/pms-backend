from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.parking.entities.rate import Rate

class IRateRepository(ABC):
    @abstractmethod
    async def get_active_by_type(self, vehicle_type: str, rate_type: str) -> Optional[Rate]:
        pass

    @abstractmethod
    async def get_by_id(self, rate_id: int) -> Optional[Rate]:
        pass

    @abstractmethod
    async def list_active(self) -> List[Rate]:
        pass

    @abstractmethod
    async def create(self, rate: Rate) -> Rate:
        pass

    @abstractmethod
    async def update(self, rate_id: int, rate: Rate) -> Rate:
        pass

    @abstractmethod
    async def delete(self, rate_id: int) -> bool:
        pass
