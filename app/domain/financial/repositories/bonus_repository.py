from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import date
from app.domain.financial.entities.bonus import Bonus

class BonusRepository(ABC):
    @abstractmethod
    async def create(self, bonus: Bonus) -> Bonus:
        """Crea un nuevo registro de bono."""
        pass

    @abstractmethod
    async def get_by_washer_and_date(self, washer_id: int, bonus_date: date) -> Optional[Bonus]:
        """Obtiene un bono por lavador y fecha."""
        pass

    @abstractmethod
    async def get_by_date(self, bonus_date: date) -> List[Bonus]:
        """Obtiene todos los bonos de una fecha."""
        pass

    @abstractmethod
    async def get_monthly_summary(self, month: int, year: int) -> List[dict]:
        """Obtiene el resumen mensual de bonos agrupado por lavador."""
        pass

    @abstractmethod
    async def get_sum_by_date_range(self, start_date: date, end_date: date) -> int:
        """Calcula la suma de bonos en un rango de fechas."""
        pass

    @abstractmethod
    async def get_daily_bonuses(self, start_date: date, end_date: date) -> List[dict]:
        """Obtiene los bonos agrupados por día en un rango de fechas.
        Retorna lista de dicts: {'date': date, 'total': int}
        """
        pass
