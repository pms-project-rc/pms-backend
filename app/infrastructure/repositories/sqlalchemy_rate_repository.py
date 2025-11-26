"""
SQLAlchemy implementation of rate repository.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.parking.value_objects.vehicle_type import VehicleType
from app.domain.parking.repositories.rate_repository import IRateRepository
from app.infrastructure.database.models.services import Rate


class SQLAlchemyRateRepository(IRateRepository):
    """
    SQLAlchemy implementation of rate repository.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def find_active_rate(
        self,
        vehicle_type: VehicleType,
        rate_type: str = "Hora"
    ) -> Optional[dict]:
        """Find active rate for a vehicle type."""
        # In the new schema, we just query by vehicle_type
        stmt = select(Rate).where(Rate.vehicle_type == vehicle_type)
        
        result = await self.session.execute(stmt)
        rate = result.scalar_one_or_none()
        
        if not rate:
            return None
        
        # Map the new schema to the expected dictionary format
        # We use parking_rate_per_minute as the default price for now
        # Convert from DB (Pesos) to Domain (Cents)
        price = int(rate.parking_rate_per_minute * 100) if rate.parking_rate_per_minute else 0
        helmet_fee = int(rate.helmet_fee * 100) if rate.helmet_fee else 0
        
        return {
            "id": rate.id,
            "vehicle_type": rate.vehicle_type,
            "rate_type": "Minute",
            "price": price,
            "helmet_fee": helmet_fee,
            "description": f"Tarifa por minuto para {vehicle_type.value}",
            "is_active": True,
        }
    
    async def get_default_rate(self) -> Optional[dict]:
        """Get default parking rate."""
        # Get the first available rate
        stmt = select(Rate).limit(1)
        
        result = await self.session.execute(stmt)
        rate = result.scalar_one_or_none()
        
        if not rate:
            return None
        
        price = int(rate.parking_rate_per_minute * 100) if rate.parking_rate_per_minute else 0
        helmet_fee = int(rate.helmet_fee * 100) if rate.helmet_fee else 0
        
        return {
            "id": rate.id,
            "vehicle_type": rate.vehicle_type,
            "rate_type": "Minute",
            "price": price,
            "helmet_fee": helmet_fee,
            "description": "Tarifa por defecto",
            "is_active": True,
        }
