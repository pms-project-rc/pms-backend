from app.domain.washers.repositories.washer_repository import IWasherRepository

class UpdateAllWashersCommission:
    def __init__(self, repository: IWasherRepository):
        self.repository = repository

    async def execute(self, percentage: int):
        if not (0 <= percentage <= 100):
            raise ValueError("Percentage must be between 0 and 100")
        
        await self.repository.update_all_commission(percentage)
