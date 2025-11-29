from app.domain.washers.repositories.washer_repository import IWasherRepository
from app.domain.washers.entities.washer import Washer
from app.application.dto.washers.washer_request import WasherUpdateRequest


class UpdateWasher:

    def __init__(self, repo: IWasherRepository):
        self.repo = repo

    async def execute(self, washer_id: int, data: WasherUpdateRequest):
        washer = await self.repo.get(washer_id)
        if not washer:
            raise ValueError(f"Washer with id {washer_id} not found")

        if data.full_name is not None:
            washer.full_name = data.full_name
        if data.email is not None:
            washer.email = data.email
        if data.phone is not None:
            washer.phone = data.phone
        if data.commission_percentage is not None:
            washer.commission_percentage = data.commission_percentage
        if data.is_active is not None:
            washer.is_active = data.is_active

        return await self.repo.update(washer_id, washer)