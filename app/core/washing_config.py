from typing import Dict, Optional

class WashingServiceConfig:
    """Configuration for washing services and their free parking minutes"""
    
    # Format: {vehicle_type: {service_name: free_minutes}}
    _FREE_MINUTES = {
        "carro": {
            "Lavado general": 30,
            "Lavado con cera": 45,
            "Lavado interior": 45,
            "Lavado de motor": 30,
            "Polishado": 60
        },
        "moto": {
            "Lavado general": 20,
            "Lavado y desengrasado": 30,
            "Lavado de motor": 20,
            "Polishado": 45
        },
        "camion": {
            "Lavado general exterior": 45,
            "Lavado de cabina interior": 45,
            "Lavado de chasis": 30,
            "Lavado de motor": 30,
            "Polishado de cabina": 60
        }
    }
    
    @classmethod
    def get_free_minutes(cls, vehicle_type: str, service_name: str) -> int:
        """Get free parking minutes for a specific vehicle type and service (case-insensitive)"""
        vehicle_config = cls._FREE_MINUTES.get(vehicle_type.lower())
        if not vehicle_config:
            return 0
            
        # Case-insensitive lookup for service name
        service_name_lower = service_name.lower()
        for name, minutes in vehicle_config.items():
            if name.lower() == service_name_lower:
                return minutes
                
        return 0
