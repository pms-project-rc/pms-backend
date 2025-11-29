from app.domain.washers.repositories.washer_repository import IWasherRepository


class GetWasher:

    def __init__(self, repo: IWasherRepository):
        self.repo = repo

    async def execute(self, washer_id: int):
        return await self.repo.get(washer_id)