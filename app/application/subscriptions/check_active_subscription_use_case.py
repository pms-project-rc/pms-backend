from datetime import date
from typing import Optional
from app.domain.subscriptions.entities.monthly_subscription import MonthlySubscription
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository

class CheckActiveSubscriptionUseCase:
    """Use case for checking if a vehicle has an active subscription"""
    
    def __init__(
        self,
        subscription_repo: ISubscriptionRepository,
        vehicle_repo: IVehicleRepository
    ):
        self.subscription_repo = subscription_repo
        self.vehicle_repo = vehicle_repo
    
    async def execute(self, plate: str) -> Optional[MonthlySubscription]:
        plate = plate.upper().strip()
        
        vehicle = await self.vehicle_repo.get_by_plate(plate)
        if not vehicle:
            return None
            
        return await self.subscription_repo.get_active_by_vehicle_id(vehicle.id, date.today())
