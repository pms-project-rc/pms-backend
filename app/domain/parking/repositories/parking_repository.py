"""
Repository interface for parking operations.
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from ..entities.parking_entry import ParkingEntry


class IParkingRepository(ABC):
    """
    Abstract repository interface for parking operations.
    
    Follows the Repository Pattern from DDD to decouple domain logic
    from infrastructure concerns.
    """
    
    @abstractmethod
    async def create_parking_entry(
        self,
        entry: ParkingEntry,
        vehicle_id: int,
        rate_id: int,
    ) -> int:
        """
        Create a new parking record.
        
        Args:
            entry: Parking entry domain entity
            vehicle_id: ID of the vehicle
            rate_id: ID of the applicable rate
            
        Returns:
            int: ID of the created parking record
        """
        pass
    
    @abstractmethod
    async def find_active_by_vehicle(self, vehicle_id: int) -> Optional[dict]:
        """
        Find active (not exited) parking record for a vehicle.
        
        Args:
            vehicle_id: ID of the vehicle
            
        Returns:
            Optional[dict]: Active parking record or None
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, parking_id: int) -> Optional[dict]:
        """
        Get parking record by ID.
        
        Args:
            parking_id: ID of the parking record
            
        Returns:
            Optional[dict]: Parking record or None
        """
        pass
    
    @abstractmethod
    async def get_all_active(self) -> List[dict]:
        """
        Get all active parking records (vehicles currently parked).
        
        Returns:
            List[dict]: List of active parking records
        """
        pass
