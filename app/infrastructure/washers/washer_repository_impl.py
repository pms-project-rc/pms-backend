from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.domain.washers.entities.washer import Washer
from app.domain.washers.repositories.washer_repository import IWasherRepository
from app.infrastructure.database.session import get_session
from app.infrastructure.database.models.users import Washer as WasherModel


class WasherRepositoryImpl(IWasherRepository):

    async def create(self, washer: Washer) -> Washer:
        async with get_session() as session:
            # Map Domain Entity -> DB Model
            # Note: Generating dummy email/password as they are required by DB but missing in Entity
            db_washer = WasherModel(
                full_name=washer.name,
                commission_percentage=int(washer.bonus_percentage),
                is_active=washer.active,
                email=f"{washer.name.replace(' ', '.').lower()}@example.com",
                password_hash="hashed_password_placeholder"
            )
            session.add(db_washer)
            await session.commit()
            await session.refresh(db_washer)
            
            return self._to_entity(db_washer)

    async def list(self) -> List[Washer]:
        async with get_session() as session:
            result = await session.execute(select(WasherModel))
            db_washers = result.scalars().all()
            return [self._to_entity(w) for w in db_washers]

    async def get(self, washer_id: int) -> Optional[Washer]:
        async with get_session() as session:
            result = await session.execute(
                select(WasherModel).where(WasherModel.id == washer_id)
            )
            db_washer = result.scalar_one_or_none()
            return self._to_entity(db_washer) if db_washer else None

    async def update(self, washer_id: int, washer: Washer) -> Washer:
        async with get_session() as session:
            # Check if exists first
            result = await session.execute(
                select(WasherModel).where(WasherModel.id == washer_id)
            )
            db_washer = result.scalar_one_or_none()
            
            if not db_washer:
                raise Exception(f"Washer with id {washer_id} not found")

            # Update fields
            db_washer.full_name = washer.name
            db_washer.commission_percentage = int(washer.bonus_percentage)
            db_washer.is_active = washer.active
            
            await session.commit()
            await session.refresh(db_washer)
            return self._to_entity(db_washer)

    async def delete(self, washer_id: int):
        async with get_session() as session:
            await session.execute(
                delete(WasherModel).where(WasherModel.id == washer_id)
            )
            await session.commit()

    def _to_entity(self, db_washer: WasherModel) -> Washer:
        return Washer(
            id=db_washer.id,
            name=db_washer.full_name,
            bonus_percentage=float(db_washer.commission_percentage),
            active=db_washer.is_active
        )
