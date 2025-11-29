from app.domain.washers.repositories.washer_repository import IWasherRepository


class ListWashers:

    def __init__(self, repo: IWasherRepository):
        self.repo = repo

    async def execute(self):
        return await self.repo.list()
