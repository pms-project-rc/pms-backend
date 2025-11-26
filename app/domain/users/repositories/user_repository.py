from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.users.entities.user import User


class UsersRepository(ABC):

    @abstractmethod
    async def create(self, user: User) -> User:
        pass

    @abstractmethod
    async def get_by_id(self, user_id: int) -> Optional[User]:
        pass

    @abstractmethod
    async def list_all(self) -> List[User]:
        pass

    @abstractmethod
    async def update(self, user_id: int, new_data: dict) -> Optional[User]:
        pass

    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        pass
