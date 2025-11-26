from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.domain.users.entities.user import User
from app.domain.users.repositories.user_repository import IUsersRepository


class UserRepositoryImpl(IUsersRepository):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user: User) -> User:
        """Crear un usuario en la BD."""
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: int) -> User | None:
        """Obtener un usuario por su ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[User]:
        """Listar todos los usuarios."""
        result = await self.session.execute(select(User))
        return result.scalars().all()

    async def update(self, user_id: int, new_data: dict) -> User | None:
        """Actualizar un usuario por ID."""
        await self.session.execute(
            update(User)
            .where(User.id == user_id)
            .values(**new_data)
        )
        await self.session.commit()

        return await self.get_by_id(user_id)

    async def delete(self, user_id: int) -> bool:
        """Eliminar un usuario por ID."""
        await self.session.execute(
            delete(User).where(User.id == user_id)
        )
        await self.session.commit()
        return True
