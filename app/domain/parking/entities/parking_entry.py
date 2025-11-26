"""
Domain entity for parking entry with business logic.
"""
from datetime import datetime
from typing import Optional

from ..value_objects.vehicle_plate import VehiclePlate
from ..value_objects.vehicle_type import VehicleType


class ParkingEntry:
    """
    Domain entity representing a parking entry.
    
    Encapsulates business rules for:
    - Helmet charge calculation (HU-07)
    - Entry validation
    - Vehicle classification
    """
    
    # Business rule: Helmet charge amount (in COP cents)
    HELMET_CHARGE_AMOUNT = 100000  # $1,000 COP = 100,000 cents
    
    def __init__(
        self,
        plate: VehiclePlate,
        entry_time: datetime,
        vehicle_type: Optional[VehicleType] = None,
        helmet_count: int = 0,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
        notes: Optional[str] = None,
        helmet_unit_price: int = 0,
    ):
        """
        Initialize a parking entry.
        
        Args:
            plate: Vehicle license plate
            entry_time: Entry timestamp
            vehicle_type: Vehicle type (if None, auto-classified from plate)
            helmet_count: Number of helmets (only for motorcycles)
            owner_name: Vehicle owner name
            owner_phone: Vehicle owner phone
            notes: Additional notes
            helmet_unit_price: Price per helmet in cents
        """
        self.plate = plate
        self.entry_time = entry_time
        self.vehicle_type = vehicle_type or plate.classified_vehicle_type
        self.helmet_count = self._validate_helmet_count(helmet_count)
        self.owner_name = owner_name
        self.owner_phone = owner_phone
        self.notes = notes
        self.helmet_unit_price = helmet_unit_price
    
    def _validate_helmet_count(self, helmet_count: int) -> int:
        """
        Validate helmet count.
        
        Business Rule: Helmet count must be non-negative and reasonable (max 3).
        """
        if helmet_count < 0:
            raise ValueError("El número de cascos no puede ser negativo")
        
        if helmet_count > 3:
            raise ValueError("El número de cascos no puede ser mayor a 3")
        
        # If vehicle is not a motorcycle, helmet count must be 0
        if not self.vehicle_type.supports_helmets and helmet_count > 0:
            raise ValueError(
                f"Los cascos solo aplican para motocicletas, "
                f"no para {self.vehicle_type.display_name}"
            )
        
        return helmet_count
    
    @property
    def helmet_charge(self) -> int:
        """
        Calculate helmet charge based on business rules.
        
        Business Rule (HU-07):
        - Only motorcycles can have helmet charges
        - Charge = helmet_unit_price per helmet
        
        Returns:
            int: Helmet charge in COP cents
        """
        if not self.vehicle_type.supports_helmets:
            return 0
        
        return self.helmet_count * self.helmet_unit_price
    
    @property
    def has_helmet_charge(self) -> bool:
        """Returns True if this entry has helmet charges."""
        return self.helmet_charge > 0
    
    def can_override_vehicle_type(self, new_type: VehicleType) -> bool:
        """
        Check if vehicle type can be manually overridden (HU-09).
        
        Business Rule: Vehicle type can always be manually corrected.
        """
        return True
    
    def override_vehicle_type(self, new_type: VehicleType) -> None:
        """
        Manually override the automatically classified vehicle type (HU-09).
        
        Args:
            new_type: New vehicle type
            
        Raises:
            ValueError: If helmet count is incompatible with new type
        """
        # Validate helmet count compatibility
        if self.helmet_count > 0 and not new_type.supports_helmets:
            raise ValueError(
                f"No se puede cambiar a {new_type.display_name} "
                f"porque hay {self.helmet_count} casco(s) registrado(s)"
            )
        
        self.vehicle_type = new_type
    
    def __repr__(self) -> str:
        return (
            f"ParkingEntry(plate='{self.plate}', "
            f"type={self.vehicle_type}, "
            f"helmets={self.helmet_count})"
        )
