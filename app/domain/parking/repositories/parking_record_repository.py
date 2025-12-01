from abc import ABC, abstractmethod
from typing import Optional, List
from datetime import date # Added import for date
from app.domain.parking.entities.parking_record import ParkingRecord

class IParkingRecordRepository(ABC):
    @abstractmethod
    async def create(self, record: ParkingRecord) -> ParkingRecord:
        pass

    @abstractmethod
    async def get_by_id(self, record_id: int) -> Optional[ParkingRecord]:
        pass

    @abstractmethod
    async def update(self, record_id: int, record: ParkingRecord) -> ParkingRecord:
        pass

    @abstractmethod
    async def get_active_by_vehicle_id(self, vehicle_id: int) -> Optional[ParkingRecord]:
        pass

    @abstractmethod
    async def list_active(self) -> List[ParkingRecord]:
        pass
