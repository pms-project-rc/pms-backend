from abc import ABC, abstractmethod
from typing import List
from datetime import datetime
from app.domain.parking.entities.parking_record import ParkingRecord

class OccupancyReportingRepository(ABC):
    @abstractmethod
    async def get_parking_records_overlapping(self, start_time: datetime, end_time: datetime) -> List[ParkingRecord]:
        """
        Obtiene los registros de parqueo que se solapan con el rango de tiempo dado.
        Es decir, vehículos que estuvieron parqueados en algún momento entre start_time y end_time.
        """
        pass

    @abstractmethod
    async def get_total_parking_duration_seconds(self, start_time: datetime, end_time: datetime) -> float:
        """
        Calcula la suma total de segundos que los vehículos estuvieron parqueados dentro del rango dado.
        Útil para calcular ocupación promedio.
        """
        pass
