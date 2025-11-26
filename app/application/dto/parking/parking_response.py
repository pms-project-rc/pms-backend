"""
Response DTOs for parking operations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class VehicleInfo(BaseModel):
    """Vehicle information in response."""
    
    id: int
    plate: str
    vehicle_type: str
    owner_name: str
    owner_phone: Optional[str] = None


class ParkingEntryResponse(BaseModel):
    """Response DTO for parking entry registration."""
    
    parking_id: int = Field(..., description="Parking record ID")
    vehicle: VehicleInfo = Field(..., description="Vehicle information")
    entry_time: datetime = Field(..., description="Entry timestamp")
    helmet_count: int = Field(default=0, description="Number of helmets")
    helmet_charge: int = Field(default=0, description="Helmet charge in COP cents")
    total_cost: int = Field(default=0, description="Total cost in COP cents")
    payment_status: str = Field(default="pending", description="Payment status")
    message: str = Field(..., description="Success message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "parking_id": 1,
                "vehicle": {
                    "id": 1,
                    "plate": "ABC123D",
                    "vehicle_type": "MOTORCYCLE",
                    "owner_name": "Juan Pérez",
                    "owner_phone": "3001234567"
                },
                "entry_time": "2025-11-25T20:00:00",
                "helmet_count": 2,
                "helmet_charge": 200000,
                "total_cost": 200000,
                "payment_status": "pending",
                "message": "Vehículo registrado exitosamente en el parqueadero"
            }
        }


class ActiveParkingItem(BaseModel):
    """Single active parking record."""
    
    parking_id: int
    vehicle_plate: str
    vehicle_type: str
    entry_time: datetime
    helmet_count: int = 0
    total_cost: int = 0


class ActiveParkingResponse(BaseModel):
    """Response DTO for active parking list."""
    
    count: int = Field(..., description="Number of active parking records")
    vehicles: list[ActiveParkingItem] = Field(..., description="List of parked vehicles")
    
    class Config:
        json_schema_extra = {
            "example": {
                "count": 2,
                "vehicles": [
                    {
                        "parking_id": 1,
                        "vehicle_plate": "ABC123D",
                        "vehicle_type": "MOTORCYCLE",
                        "entry_time": "2025-11-25T20:00:00",
                        "helmet_count": 2,
                        "total_cost": 200000
                    },
                    {
                        "parking_id": 2,
                        "vehicle_plate": "XYZ789",
                        "vehicle_type": "CAR",
                        "entry_time": "2025-11-25T20:15:00",
                        "helmet_count": 0,
                        "total_cost": 0
                    }
                ]
            }
        }
