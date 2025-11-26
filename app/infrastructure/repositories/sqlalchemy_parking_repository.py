"""
SQLAlchemy implementation of parking repository.
"""
from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.parking.entities.parking_entry import ParkingEntry
from app.domain.parking.repositories.parking_repository import IParkingRepository
from app.infrastructure.database.models.vehicles import ParkingRecord


class SQLAlchemyParkingRepository(IParkingRepository):
    """
    SQLAlchemy implementation of parking repository.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_parking_entry(
        self,
        entry: ParkingEntry,
        vehicle_id: int,
        rate_id: int,
    ) -> int:
        """Create a new parking record."""
        parking_record = ParkingRecord(
            vehicle_id=vehicle_id,
            entry_time=entry.entry_time,
            parking_rate_id=rate_id,
            helmet_count=entry.helmet_count,
            helmet_charge=entry.helmet_charge,
            total_cost=entry.helmet_charge,  # Initial cost is just helmet charge
            payment_status="pending",
            notes=entry.notes,
        )
        
        self.session.add(parking_record)
        await self.session.flush()
        
        return parking_record.id
    
    async def find_active_by_vehicle(self, vehicle_id: int) -> Optional[dict]:
        """Find active parking record for a vehicle."""
        stmt = select(ParkingRecord).where(
            ParkingRecord.vehicle_id == vehicle_id,
            ParkingRecord.exit_time.is_(None)
        )
        
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        
        if not record:
            return None
        
        return {
            "id": record.id,
            "vehicle_id": record.vehicle_id,
            "entry_time": record.entry_time,
            "exit_time": record.exit_time,
            "parking_rate_id": record.parking_rate_id,
            "helmet_count": getattr(record, "helmet_count", 0),
            "helmet_charge": getattr(record, "helmet_charge", 0),
            "total_cost": record.total_cost,
            "payment_status": record.payment_status,
            "notes": record.notes,
        }
    
    async def get_by_id(self, parking_id: int) -> Optional[dict]:
        """Get parking record by ID."""
        stmt = select(ParkingRecord).where(ParkingRecord.id == parking_id)
        
        result = await self.session.execute(stmt)
        record = result.scalar_one_or_none()
        
        if not record:
            return None
        
        return {
            "id": record.id,
            "vehicle_id": record.vehicle_id,
            "entry_time": record.entry_time,
            "exit_time": record.exit_time,
            "parking_rate_id": record.parking_rate_id,
            "helmet_count": getattr(record, "helmet_count", 0),
            "helmet_charge": getattr(record, "helmet_charge", 0),
            "total_cost": record.total_cost,
            "payment_status": record.payment_status,
            "notes": record.notes,
        }
    
    async def get_all_active(self) -> List[dict]:
        """Get all active parking records."""
        stmt = select(ParkingRecord).where(
            ParkingRecord.exit_time.is_(None)
        ).order_by(ParkingRecord.entry_time.desc())
        
        result = await self.session.execute(stmt)
        records = result.scalars().all()
        
        return [
            {
                "id": record.id,
                "vehicle_id": record.vehicle_id,
                "entry_time": record.entry_time,
                "parking_rate_id": record.parking_rate_id,
                "helmet_count": getattr(record, "helmet_count", 0),
                "helmet_charge": getattr(record, "helmet_charge", 0),
                "total_cost": record.total_cost,
                "payment_status": record.payment_status,
            }
            for record in records
        ]
