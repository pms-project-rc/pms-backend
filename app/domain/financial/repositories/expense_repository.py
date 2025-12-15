from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.financial.entities.expense import Expense
from datetime import date

class ExpenseRepository(ABC):
    @abstractmethod
    async def save(self, expense: Expense) -> Expense:
        """Guarda un gasto (crear o actualizar)."""
        pass

    @abstractmethod
    async def get_by_id(self, expense_id: int) -> Optional[Expense]:
        """Obtiene un gasto por su ID."""
        pass

    @abstractmethod
    async def delete(self, expense_id: int) -> None:
        """Elimina un gasto por su ID."""
        pass

    @abstractmethod
    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Expense]:
        """Obtiene gastos en un rango de fechas."""
        pass

    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Expense]:
        """Obtiene todos los gastos con paginación."""
        pass

    @abstractmethod
    async def get_total_by_shift(self, shift_id: int) -> int:
        """Calcula el total de gastos para un turno."""
        pass

    @abstractmethod
    async def get_sum_by_date_range(self, start_date: date, end_date: date) -> int:
        """Calcula la suma de gastos en un rango de fechas."""
        pass

    @abstractmethod
    async def get_daily_expenses(self, start_date: date, end_date: date) -> List[dict]:
        """Obtiene los gastos agrupados por día en un rango de fechas.
        Retorna lista de dicts: {'date': date, 'total': int}
        """
        pass
