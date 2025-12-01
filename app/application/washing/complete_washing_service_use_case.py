from datetime import datetime, timezone
from typing import Optional
from app.domain.washing.entities.washing_service import WashingService
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository

class CompleteWashingServiceUseCase:
    """Use case for completing a washing service"""
    
    def __init__(self, washing_repo: IWashingServiceRepository):
        self.washing_repo = washing_repo
    
    async def execute(
        self,
        service_id: int,
        notes: Optional[str] = None
    ) -> WashingService:
        # Check if service exists
        service = await self.washing_repo.get_by_id(service_id)
        if not service:
            raise ValueError(f"Washing service with ID {service_id} not found")
            
        if service.payment_status == "paid":
            raise ValueError("Service is already paid and completed")
            
        # Complete service
        service.end_time = datetime.now(timezone.utc)
        service.payment_status = "paid"
        
        if notes:
            service.notes = notes
            
        return await self.washing_repo.update(service.id, service)
