from app.domain.users.repositories.user_repository import IUsersRepository
from app.domain.users.entities.user import User
from app.application.dto.users.user_request import UserCreateRequest

class CreateUser:
    def __init__(self, repo: IUsersRepository):
        self.repo = repo

    async def execute(self, data: UserCreateRequest) -> User:
        user = User(
            id=None,
            full_name=data.full_name,
            email=data.email,
            phone=data.phone,
            status=data.status
        )
        return await self.repo.create(user)
