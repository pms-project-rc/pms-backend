"""
Repository interface for vehicle operations.
"""
from abc import ABC, abstractmethod
from typing import Optional

from ..value_objects.vehicle_plate import VehiclePlate
from ..value_objects.vehicle_type import VehicleType


class IVehicleRepository(ABC):
    """
    Abstract repository interface for vehicle operations.
    """
    
    @abstractmethod
    async def find_by_plate(self, plate: VehiclePlate) -> Optional[dict]:
        """
        Find vehicle by license plate.
        
        Args:
            plate: Vehicle license plate
            
        Returns:
            Optional[dict]: Vehicle data or None
        """
        pass
    
    @abstractmethod
    async def create_vehicle(
        self,
        plate: VehiclePlate,
        vehicle_type: VehicleType,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
    ) -> int:
        """
        Create a new vehicle record.
        
        Args:
            plate: Vehicle license plate
            vehicle_type: Type of vehicle
            owner_name: Owner name (optional)
            owner_phone: Owner phone (optional)
            
        Returns:
            int: ID of the created vehicle
        """
        pass
    
    @abstractmethod
    async def update_vehicle(
        self,
        vehicle_id: int,
        vehicle_type: Optional[VehicleType] = None,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
    ) -> bool:
        """
        Update vehicle information.
        
        Args:
            vehicle_id: ID of the vehicle
            vehicle_type: New vehicle type (optional)
            owner_name: New owner name (optional)
            owner_phone: New owner phone (optional)
            
        Returns:
            bool: True if updated successfully
        """
        pass
