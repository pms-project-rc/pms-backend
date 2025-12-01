from typing import Optional, List
from datetime import date
from sqlalchemy import select, update, func
from app.domain.parking.entities.parking_record import ParkingRecord
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.vehicles import ParkingRecord as ParkingRecordModel

class ParkingRecordRepositoryImpl(IParkingRecordRepository):
    
    def _to_entity(self, model: ParkingRecordModel) -> Optional[ParkingRecord]:
        if not model:
            return None
        return ParkingRecord(
            id=model.id,
            vehicle_id=model.vehicle_id,
            shift_id=model.shift_id,
            admin_id=model.admin_id,
            entry_time=model.entry_time,
            parking_rate_id=model.parking_rate_id,
            exit_time=model.exit_time,
            subscription_id=model.subscription_id,
            washing_service_id=model.washing_service_id,
            helmet_count=model.helmet_count,
            helmet_charge=model.helmet_charge,
            total_cost=model.total_cost,
            payment_status=model.payment_status,
            notes=model.notes
        )

    def _to_model(self, entity: ParkingRecord) -> ParkingRecordModel:
        return ParkingRecordModel(
            id=entity.id,
            vehicle_id=entity.vehicle_id,
            shift_id=entity.shift_id,
            admin_id=entity.admin_id,
            entry_time=entity.entry_time,
            parking_rate_id=entity.parking_rate_id,
            exit_time=entity.exit_time,
            subscription_id=entity.subscription_id,
            washing_service_id=entity.washing_service_id,
            helmet_count=entity.helmet_count,
            helmet_charge=entity.helmet_charge,
            total_cost=entity.total_cost,
            payment_status=entity.payment_status,
            notes=entity.notes
        )

    async def create(self, record: ParkingRecord) -> ParkingRecord:
        async with SessionLocal() as session:
            model = self._to_model(record)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, record_id: int) -> Optional[ParkingRecord]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ParkingRecordModel).where(ParkingRecordModel.id == record_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def update(self, record_id: int, record: ParkingRecord) -> ParkingRecord:
        async with SessionLocal() as session:
            # We construct the update statement dynamically or just update all fields
            # For simplicity, let's update relevant fields
            stmt = (
                update(ParkingRecordModel)
                .where(ParkingRecordModel.id == record_id)
                .values(
                    exit_time=record.exit_time,
                    total_cost=record.total_cost,
                    payment_status=record.payment_status,
                    notes=record.notes,
                    washing_service_id=record.washing_service_id
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            result = await session.execute(
                select(ParkingRecordModel).where(ParkingRecordModel.id == record_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def get_active_by_vehicle_id(self, vehicle_id: int) -> Optional[ParkingRecord]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ParkingRecordModel)
                .where(ParkingRecordModel.vehicle_id == vehicle_id)
                .where(ParkingRecordModel.exit_time.is_(None))
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def list_active(self) -> List[ParkingRecord]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ParkingRecordModel)
                .where(ParkingRecordModel.exit_time.is_(None))
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def list_by_date_range(self, start_date: date, end_date: date) -> List[ParkingRecord]:
        async with SessionLocal() as session:
            # Filter by entry_time within the date range
            # We cast entry_time to date for comparison
            result = await session.execute(
                select(ParkingRecordModel)
                .where(func.date(ParkingRecordModel.entry_time) >= start_date)
                .where(func.date(ParkingRecordModel.entry_time) <= end_date)
                .order_by(ParkingRecordModel.entry_time.desc())
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def get_last_by_vehicle_id(self, vehicle_id: int, limit: int = 5) -> List[ParkingRecord]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ParkingRecordModel)
                .where(ParkingRecordModel.vehicle_id == vehicle_id)
                .order_by(ParkingRecordModel.entry_time.desc())
                .limit(limit)
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]
