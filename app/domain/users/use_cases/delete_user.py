from app.domain.users.repositories.user_repository import IUsersRepository

class DeleteUser:
    def __init__(self, repo: IUsersRepository):
        self.repo = repo

    async def execute(self, user_id: int):
        await self.repo.delete(user_id)
        return True
