from sqlalchemy import select, func, cast, Date, update
from datetime import date
from typing import List, Optional
from app.domain.washing.entities.washing_service import WashingService
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import WashingService as WashingServiceModel

class WashingServiceRepositoryImpl(IWashingServiceRepository):
    
    def _to_entity(self, model: WashingServiceModel) -> Optional[WashingService]:
        if not model:
            return None
        return WashingService(
            id=model.id,
            vehicle_id=model.vehicle_id,
            shift_id=model.shift_id,
            admin_id=model.admin_id,
            service_type=model.service_type,
            service_date=model.service_date,
            price=model.price,
            parking_record_id=model.parking_record_id,
            washer_id=model.washer_id,
            start_time=model.start_time,
            end_time=model.end_time,
            payment_status=model.payment_status,
            notes=model.notes
        )

    def _to_model(self, entity: WashingService) -> WashingServiceModel:
        return WashingServiceModel(
            id=entity.id,
            vehicle_id=entity.vehicle_id,
            shift_id=entity.shift_id,
            admin_id=entity.admin_id,
            service_type=entity.service_type,
            service_date=entity.service_date,
            price=entity.price,
            parking_record_id=entity.parking_record_id,
            washer_id=entity.washer_id,
            start_time=entity.start_time,
            end_time=entity.end_time,
            payment_status=entity.payment_status,
            notes=entity.notes
        )

    async def create(self, service: WashingService) -> WashingService:
        async with SessionLocal() as session:
            model = self._to_model(service)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, service_id: int) -> Optional[WashingService]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(WashingServiceModel).where(WashingServiceModel.id == service_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def update(self, service_id: int, service: WashingService) -> WashingService:
        async with SessionLocal() as session:
            stmt = (
                update(WashingServiceModel)
                .where(WashingServiceModel.id == service_id)
                .values(
                    washer_id=service.washer_id,
                    start_time=service.start_time,
                    end_time=service.end_time,
                    payment_status=service.payment_status,
                    notes=service.notes
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            result = await session.execute(
                select(WashingServiceModel).where(WashingServiceModel.id == service_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def list_active(self) -> List[WashingService]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(WashingServiceModel)
                .where(WashingServiceModel.end_time.is_(None))
                .order_by(WashingServiceModel.service_date.desc())
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def get_total_income_by_shift(self, shift_id: int) -> int:
        async with SessionLocal() as session:
            result = await session.execute(
                select(func.sum(WashingServiceModel.price))
                .where(WashingServiceModel.shift_id == shift_id)
                .where(WashingServiceModel.payment_status == 'paid')
            )
            total = result.scalar()
            return total if total else 0

    async def get_total_sales_by_washer_and_date(self, washer_id: int, date: str) -> int:
        async with SessionLocal() as session:
            result = await session.execute(
                select(func.sum(WashingServiceModel.price))
                .where(WashingServiceModel.washer_id == washer_id)
                .where(func.date(WashingServiceModel.created_at) == date)
                .where(WashingServiceModel.payment_status == 'paid')
            )
            total = result.scalar()
            return total if total else 0

    async def get_washing_duration_stats(self, start_date: date, end_date: date) -> List[dict]:
        async with SessionLocal() as session:
            stmt = (
                select(
                    WashingServiceModel.washer_id,
                    WashingServiceModel.service_type,
                    func.avg(WashingServiceModel.end_time - WashingServiceModel.start_time).label("avg_duration"),
                    func.count(WashingServiceModel.id).label("count")
                )
                .where(cast(WashingServiceModel.service_date, Date) >= start_date)
                .where(cast(WashingServiceModel.service_date, Date) <= end_date)
                .where(WashingServiceModel.start_time.isnot(None))
                .where(WashingServiceModel.end_time.isnot(None))
                .group_by(WashingServiceModel.washer_id, WashingServiceModel.service_type)
            )
            result = await session.execute(stmt)
            return [
                {
                    "washer_id": row.washer_id,
                    "service_type": row.service_type,
                    "avg_duration": row.avg_duration,
                    "count": row.count
                }
                for row in result
            ]
