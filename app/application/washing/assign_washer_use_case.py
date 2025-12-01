from datetime import datetime, timezone
from typing import Optional
from app.domain.washing.entities.washing_service import WashingService
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository
from app.domain.washers.repositories.washer_repository import IWasherRepository

class AssignWasherUseCase:
    """Use case for assigning a washer to a service"""
    
    def __init__(
        self,
        washing_repo: IWashingServiceRepository,
        washer_repo: IWasherRepository
    ):
        self.washing_repo = washing_repo
        self.washer_repo = washer_repo
    
    async def execute(
        self,
        service_id: int,
        washer_id: int
    ) -> WashingService:
        # Check if service exists
        service = await self.washing_repo.get_by_id(service_id)
        if not service:
            raise ValueError(f"Washing service with ID {service_id} not found")
            
        # Check if washer exists
        washer = await self.washer_repo.get(washer_id)
        if not washer:
            raise ValueError(f"Washer with ID {washer_id} not found")
            
        if not washer.is_active:
            raise ValueError(f"Washer {washer.full_name} is not active")
            
        # Assign washer and set start time if not set
        service.washer_id = washer_id
        if not service.start_time:
            service.start_time = datetime.now(timezone.utc)
            
        return await self.washing_repo.update(service.id, service)
