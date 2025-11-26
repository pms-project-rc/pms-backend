from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.users.entities.user import User
from app.domain.users.repositories.user_repository import UserRepository
from app.infrastructure.database.models.users import GlobalAdmin, OperationalAdmin, Washer

class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_username(self, username: str) -> Optional[User]:
        # Check GlobalAdmin
        stmt = select(GlobalAdmin).where(GlobalAdmin.email == username)
        result = await self.session.execute(stmt)
        admin = result.scalar_one_or_none()
        if admin:
            return User(
                id=admin.id,
                username=admin.email,
                password_hash=admin.password_hash,
                role="global_admin",
                active=admin.is_active
            )

        # Check OperationalAdmin
        stmt = select(OperationalAdmin).where(OperationalAdmin.email == username)
        result = await self.session.execute(stmt)
        op_admin = result.scalar_one_or_none()
        if op_admin:
            return User(
                id=op_admin.id,
                username=op_admin.email,
                password_hash=op_admin.password_hash,
                role="operational_admin",
                active=op_admin.is_active
            )

        # Check Washer
        stmt = select(Washer).where(Washer.email == username)
        result = await self.session.execute(stmt)
        washer = result.scalar_one_or_none()
        if washer and washer.password_hash:  # Only allow login if password is set
            return User(
                id=washer.id,
                username=washer.email,
                password_hash=washer.password_hash,
                role="washer",
                active=washer.is_active
            )

        return None

    async def save(self, user: User) -> User:
        # For now, we are not implementing save for the unified User as it maps to different tables.
        # This would require more complex logic to decide which table to insert into.
        # Since this is just for Login (Read), we can skip implementation or raise NotImplementedError
        raise NotImplementedError("Save not implemented for unified User repository yet")
