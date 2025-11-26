from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.domain.washers.entities.washer import Washer


class WasherRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, washer: Washer):
        self.session.add(washer)
        await self.session.commit()
        await self.session.refresh(washer)
        return washer

    async def list_all(self):
        result = await self.session.execute(select(Washer))
        return result.scalars().all()

    async def get_by_id(self, washer_id: int):
        result = await self.session.execute(
            select(Washer).where(Washer.id == washer_id)
        )
        return result.scalar_one_or_none()

    async def update(self, washer_id: int, data: dict):
        await self.session.execute(
            update(Washer).where(Washer.id == washer_id).values(**data)
        )
        await self.session.commit()
        return await self.get_by_id(washer_id)

    async def delete(self, washer_id: int):
        await self.session.execute(
            delete(Washer).where(Washer.id == washer_id)
        )
        await self.session.commit()
