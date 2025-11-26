from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.users.entities.user import User

class IUsersRepository(ABC):
    """
    Interfaz/contrato del repositorio de Users.
    Cualquier implementación (SQLAlchemy, database, mock) debe implementar estos métodos.
    """

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def list(self) -> List[User]:
        pass

    @abstractmethod
    async def get(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def update(self, user_id: int, user: User) -> User:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> None:
        pass
