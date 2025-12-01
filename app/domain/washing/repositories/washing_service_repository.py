from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.domain.washing.entities.washing_service import WashingService

class IWashingServiceRepository(ABC):
    @abstractmethod
    async def create(self, service: WashingService) -> WashingService:
        pass

    @abstractmethod
    async def get_by_id(self, service_id: int) -> Optional[WashingService]:
        pass

    @abstractmethod
    async def update(self, service_id: int, service: WashingService) -> WashingService:
        pass

    @abstractmethod
    async def list_active(self) -> List[WashingService]:
        pass

    @abstractmethod
    async def get_total_income_by_shift(self, shift_id: int) -> int:
        """Calcula el ingreso total de lavados para un turno."""
        pass

    @abstractmethod
    async def get_total_sales_by_washer_and_date(self, washer_id: int, date: str) -> int:
        """Calcula el total de ventas de un lavador en una fecha específica."""
        pass

    @abstractmethod
    async def get_washing_duration_stats(self, start_date: date, end_date: date) -> List[dict]:
        """Obtiene estadísticas de duración de lavados agrupadas por lavador y tipo de servicio."""
        pass

