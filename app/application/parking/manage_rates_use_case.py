from typing import List, Optional
from app.domain.parking.entities.rate import Rate
from app.domain.parking.repositories.rate_repository import IRateRepository

class ManageRatesUseCase:
    """Use case for managing parking rates"""
    
    def __init__(self, rate_repo: IRateRepository):
        self.rate_repo = rate_repo
    
    async def create_rate(
        self,
        vehicle_type: str,
        rate_type: str,
        price: int,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Rate:
        # Normalize inputs
        vehicle_type = vehicle_type.lower().strip()
        rate_type = rate_type.lower().strip()
        
        # Check if rate already exists for this type combination
        if is_active:
            existing = await self.rate_repo.get_active_by_type(vehicle_type, rate_type)
            if existing:
                # Deactivate the existing rate to avoid conflicts
                existing.is_active = False
                await self.rate_repo.update(existing.id, existing)
            
        rate = Rate(
            id=None,
            vehicle_type=vehicle_type,
            rate_type=rate_type,
            price=price,
            description=description,
            is_active=is_active
        )
        
        return await self.rate_repo.create(rate)
    
    async def update_rate(
        self,
        rate_id: int,
        vehicle_type: str,
        rate_type: str,
        price: int,
        description: Optional[str] = None,
        is_active: bool = True
    ) -> Rate:
        rate = await self.rate_repo.get_by_id(rate_id)
        if not rate:
            raise ValueError(f"Rate with ID {rate_id} not found")
            
        rate.vehicle_type = vehicle_type
        rate.rate_type = rate_type
        rate.price = price
        rate.description = description
        rate.is_active = is_active
        
        return await self.rate_repo.update(rate_id, rate)
    
    async def delete_rate(self, rate_id: int):
        rate = await self.rate_repo.get_by_id(rate_id)
        if not rate:
            raise ValueError(f"Rate with ID {rate_id} not found")
            
        await self.rate_repo.delete(rate_id)
        
    async def list_rates(self) -> List[Rate]:
        return await self.rate_repo.list_active()
