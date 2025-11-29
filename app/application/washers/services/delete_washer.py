from app.domain.washers.repositories.washer_repository import IWasherRepository


class DeleteWasher:

    def __init__(self, repo: IWasherRepository):
        self.repo = repo

    async def execute(self, washer_id: int):
        return await self.repo.delete(washer_id)