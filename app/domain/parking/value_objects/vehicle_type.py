"""
Value object for vehicle types with business rules.
"""
from enum import Enum


class VehicleType(str, Enum):
    """Enumeration of vehicle types supported by the system."""
    
    MOTORCYCLE = "moto"
    CAR = "carro"
    TRUCK = "camión"
    BICYCLE = "bicicleta"
    
    @property
    def supports_helmets(self) -> bool:
        """Returns True if this vehicle type can have helmet charges."""
        return self == VehicleType.MOTORCYCLE
    
    @property
    def display_name(self) -> str:
        """Returns a user-friendly display name."""
        display_names = {
            VehicleType.MOTORCYCLE: "Motocicleta",
            VehicleType.CAR: "Automóvil",
            VehicleType.TRUCK: "Camión",
            VehicleType.BICYCLE: "Bicicleta",
        }
        return display_names.get(self, self.value)
    
    def __str__(self) -> str:
        return self.value
