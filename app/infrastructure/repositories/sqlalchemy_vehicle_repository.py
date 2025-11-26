"""
SQLAlchemy implementation of vehicle repository.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.parking.value_objects.vehicle_plate import VehiclePlate
from app.domain.parking.value_objects.vehicle_type import VehicleType
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.infrastructure.database.models.vehicles import Vehicle


class SQLAlchemyVehicleRepository(IVehicleRepository):
    """
    SQLAlchemy implementation of vehicle repository.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_by_plate(self, plate: VehiclePlate) -> Optional[dict]:
        """Find vehicle by license plate."""
        stmt = select(Vehicle).where(Vehicle.plate == str(plate))
        
        result = await self.session.execute(stmt)
        vehicle = result.scalar_one_or_none()
        
        if not vehicle:
            return None
        
        return {
            "id": vehicle.id,
            "plate": vehicle.plate,
            "owner_name": vehicle.owner_name,
            "owner_phone": vehicle.owner_phone,
            "vehicle_type": vehicle.vehicle_type,
            "brand": vehicle.brand,
            "model": vehicle.model,
            "color": vehicle.color,
            "is_frequent": vehicle.is_frequent,
            "notes": vehicle.notes,
        }
    
    async def create_vehicle(
        self,
        plate: VehiclePlate,
        vehicle_type: VehicleType,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
    ) -> int:
        """Create a new vehicle record."""
        vehicle = Vehicle(
            plate=str(plate),
            owner_name=owner_name or "Desconocido",
            owner_phone=owner_phone,
            vehicle_type=vehicle_type.value,
            is_frequent=False,
        )
        
        self.session.add(vehicle)
        await self.session.flush()
        
        return vehicle.id
    
    async def update_vehicle(
        self,
        vehicle_id: int,
        vehicle_type: Optional[VehicleType] = None,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
    ) -> bool:
        """Update vehicle information."""
        stmt = select(Vehicle).where(Vehicle.id == vehicle_id)
        result = await self.session.execute(stmt)
        vehicle = result.scalar_one_or_none()
        
        if not vehicle:
            return False
        
        if vehicle_type is not None:
            vehicle.vehicle_type = vehicle_type.value
        
        if owner_name is not None:
            vehicle.owner_name = owner_name
        
        if owner_phone is not None:
            vehicle.owner_phone = owner_phone
        
        await self.session.flush()
        return True
