from app.domain.users.repositories.user_repository import IUsersRepository

class ListUsers:
    def __init__(self, repo: IUsersRepository):
        self.repo = repo

    async def execute(self):
        return await self.repo.list()
