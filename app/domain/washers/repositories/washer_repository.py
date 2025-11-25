from abc import ABC, abstractmethod

from app.domain.washers.entities.washer import Washer


class IWasherRepository(ABC):

    @abstractmethod
    async def create(self, washer: Washer) -> Washer:
        pass

    @abstractmethod
    async def list(self) -> list[Washer]:
        pass

    @abstractmethod
    async def get(self, washer_id: int) -> Washer | None:
        pass

    @abstractmethod
    async def update(self, washer_id: int, washer: Washer) -> Washer:
        pass

    @abstractmethod
    async def delete(self, washer_id: int):
        pass
