"""
Repository interface for rate operations.
"""
from abc import ABC, abstractmethod
from typing import Optional

from ..value_objects.vehicle_type import VehicleType


class IRateRepository(ABC):
    """
    Abstract repository interface for rate operations.
    """
    
    @abstractmethod
    async def find_active_rate(
        self,
        vehicle_type: VehicleType,
        rate_type: str = "Hora"
    ) -> Optional[dict]:
        """
        Find active rate for a vehicle type.
        
        Args:
            vehicle_type: Type of vehicle
            rate_type: Type of rate (default: "Hora")
            
        Returns:
            Optional[dict]: Rate data or None
        """
        pass
    
    @abstractmethod
    async def get_default_rate(self) -> Optional[dict]:
        """
        Get default parking rate.
        
        Returns:
            Optional[dict]: Default rate or None
        """
        pass
