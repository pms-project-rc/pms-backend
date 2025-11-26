from app.domain.users.repositories.user_repository import UsersRepository

class ListUsers:
    def __init__(self, repository: UsersRepository):
        self.repo = repo

    async def execute(self):
        return await self.repo.list()
