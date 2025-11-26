from abc import ABC, abstractmethod
from app.domain.users.entities.user import User

class IUsersRepository(ABC):

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        pass

    @abstractmethod
    async def list(self) -> list[User]:
        pass

    @abstractmethod
    async def update(self, user_id: int, user: User) -> User | None:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass
