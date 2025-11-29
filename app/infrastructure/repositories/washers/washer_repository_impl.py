from typing import List, Optional
from sqlalchemy import select, update, delete, func

from app.domain.washers.entities.washer import Washer
from app.domain.washers.repositories.washer_repository import IWasherRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import Washer as WasherModel


class WasherRepositoryImpl(IWasherRepository):

    def _to_entity(self, model: WasherModel) -> Optional[Washer]:
        if not model:
            return None
        return Washer(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            phone=model.phone,
            commission_percentage=model.commission_percentage,
            is_active=model.is_active,
            password_hash=model.password_hash
        )

    def _to_model(self, entity: Washer) -> WasherModel:
        return WasherModel(
            id=entity.id,
            full_name=entity.full_name,
            email=entity.email,
            phone=entity.phone,
            commission_percentage=entity.commission_percentage,
            is_active=entity.is_active,
            password_hash=entity.password_hash
        )

    async def create(self, washer: Washer) -> Washer:
        async with SessionLocal() as session:
            model = self._to_model(washer)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def list(self) -> List[Washer]:
        async with SessionLocal() as session:
            result = await session.execute(select(WasherModel))
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def get(self, washer_id: int) -> Optional[Washer]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(WasherModel).where(WasherModel.id == washer_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def update(self, washer_id: int, washer: Washer) -> Washer:
        async with SessionLocal() as session:
            stmt = (
                update(WasherModel)
                .where(WasherModel.id == washer_id)
                .values(
                    full_name=washer.full_name,
                    email=washer.email,
                    phone=washer.phone,
                    commission_percentage=washer.commission_percentage,
                    is_active=washer.is_active,
                    password_hash=washer.password_hash
                )
            )
            await session.execute(stmt)
            await session.commit()

            result = await session.execute(
                select(WasherModel).where(WasherModel.id == washer_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def delete(self, washer_id: int):
        async with SessionLocal() as session:
            await session.execute(
                delete(WasherModel).where(WasherModel.id == washer_id)
            )
            await session.commit()

    async def update_all_commission(self, percentage: int):
        async with SessionLocal() as session:
            stmt = (
                update(WasherModel)
                .values(commission_percentage=percentage)
            )
            await session.execute(stmt)
            await session.commit()

    async def count_active(self) -> int:
        async with SessionLocal() as session:
            result = await session.execute(
                select(func.count(WasherModel.id)).where(WasherModel.is_active == True)
            )
            return result.scalar() or 0
