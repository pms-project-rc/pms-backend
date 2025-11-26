from app.domain.users.repositories.user_repository import UsersRepository


class DeleteUser:

    def __init__(self, repository: UsersRepository):
        self.repository = repository

    async def execute(self, user_id: int) -> bool:
        return await self.repository.delete(user_id)
