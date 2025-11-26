from app.domain.users.repositories.user_repository import UsersRepository
from app.domain.users.entities.user import User

class CreateUser:

    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def execute(self, data):
        user = User(
            name=data.name,
            email=data.email,
            phone=data.phone,
            role=data.role,
        )
        return await self.repository.create(user)
