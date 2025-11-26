from app.domain.users.repositories.user_repository import UsersRepository

class GetUser:
    def __init__(self, repo: UsersRepository):
        self.repo = repo

    async def execute(self, user_id: int):
        return await self.repo.get(user_id)
