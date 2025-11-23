"""
Interfaz del repositorio para Washers (Puerto).

Define el contrato que deben cumplir las implementaciones concretas.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.washers.entities import Washer


class WasherRepository(ABC):
    """
    Interfaz del repositorio de Washers.
    
    Define las operaciones de persistencia para la entidad Washer.
    """
    
    @abstractmethod
    async def save(self, washer: Washer) -> Washer:
        """Guarda o actualiza un Washer."""
        pass
    
    @abstractmethod
    async def find_by_id(self, washer_id: int) -> Optional[Washer]:
        """Busca un Washer por ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Washer]:
        """Busca un Washer por email."""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Washer]:
        """Obtiene todos los Washers con paginación."""
        pass
    
    @abstractmethod
    async def find_active(self) -> List[Washer]:
        """Obtiene todos los Washers activos."""
        pass
    
    @abstractmethod
    async def find_by_commission_range(
        self,
        min_commission: int,
        max_commission: int
    ) -> List[Washer]:
        """Busca lavadores por rango de comisión."""
        pass
    
    @abstractmethod
    async def delete(self, washer_id: int) -> bool:
        """Elimina un Washer."""
        pass
