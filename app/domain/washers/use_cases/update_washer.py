from app.application.dto.washers.washer_request import WasherUpdateRequest
from app.domain.washers.entities.washer import Washer
from app.domain.washers.repositories.washer_repository import IWasherRepository


class UpdateWasher:

    def __init__(self, repo: IWasherRepository):
        self.repo = repo

    async def execute(self, washer_id: int, data: WasherUpdateRequest):
        washer = Washer(
            id=washer_id,
            name=data.name,
            phone=data.phone,
            status=data.status
        )
        return await self.repo.update(washer_id, washer)
