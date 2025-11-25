from app.application.dto.washers.washer_request import WasherCreateRequest
from app.domain.washers.entities.washer import Washer
from app.domain.washers.repositories.washer_repository import IWasherRepository


class CreateWasher:

    def __init__(self, repo: IWasherRepository):
        self.repo = repo

    async def execute(self, data: WasherCreateRequest):
        washer = Washer(
            name=data.name,
            phone=data.phone,
            status=data.status
        )
        return await self.repo.create(washer)
