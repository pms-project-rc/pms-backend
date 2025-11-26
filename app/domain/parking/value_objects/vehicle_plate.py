"""
Value object for vehicle license plates with automatic classification logic.
"""
import re
from typing import Optional

from .vehicle_type import VehicleType


class VehiclePlate:
    """
    Value object representing a vehicle license plate.
    
    Implements automatic vehicle classification based on Colombian plate format:
    - Plates ending in LETTER → Motorcycle
    - Plates ending in NUMBER → Car
    """
    
    # Colombian plate patterns
    PLATE_PATTERN = re.compile(r'^[A-Z]{3}\d{3}[A-Z]?$', re.IGNORECASE)
    
    def __init__(self, plate: str):
        """
        Initialize a vehicle plate.
        
        Args:
            plate: License plate string (e.g., "ABC123" or "ABC123D")
            
        Raises:
            ValueError: If plate format is invalid
        """
        self._plate = self._validate_and_normalize(plate)
    
    def _validate_and_normalize(self, plate: str) -> str:
        """Validate and normalize the plate format."""
        if not plate:
            raise ValueError("La placa no puede estar vacía")
        
        # Remove spaces and convert to uppercase
        normalized = plate.strip().upper().replace(" ", "").replace("-", "")
        
        # Validate format
        if not self.PLATE_PATTERN.match(normalized):
            raise ValueError(
                f"Formato de placa inválido: '{plate}'. "
                "Formato esperado: ABC123 o ABC123D"
            )
        
        return normalized
    
    @property
    def value(self) -> str:
        """Returns the normalized plate value."""
        return self._plate
    
    @property
    def classified_vehicle_type(self) -> VehicleType:
        """
        Automatically classify vehicle type based on plate format.
        
        Business Rule (HU-08):
        - Plate ending in LETTER → Motorcycle
        - Plate ending in NUMBER → Car
        
        Returns:
            VehicleType: Automatically classified vehicle type
        """
        last_char = self._plate[-1]
        
        if last_char.isalpha():
            return VehicleType.MOTORCYCLE
        else:
            return VehicleType.CAR
    
    def __str__(self) -> str:
        return self._plate
    
    def __repr__(self) -> str:
        return f"VehiclePlate('{self._plate}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, VehiclePlate):
            return False
        return self._plate == other._plate
    
    def __hash__(self) -> int:
        return hash(self._plate)
