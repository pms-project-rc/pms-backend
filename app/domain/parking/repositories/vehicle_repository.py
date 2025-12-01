from abc import ABC, abstractmethod
from typing import Optional
from app.domain.parking.entities.vehicle import Vehicle

class IVehicleRepository(ABC):
    @abstractmethod
    async def get_by_plate(self, plate: str) -> Optional[Vehicle]:
        pass

    @abstractmethod
    async def create(self, vehicle: Vehicle) -> Vehicle:
        pass

    @abstractmethod
    async def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        pass

    @abstractmethod
    async def update(self, vehicle_id: int, vehicle: Vehicle) -> Vehicle:
        pass
