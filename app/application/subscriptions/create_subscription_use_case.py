from datetime import date, timedelta
from typing import Optional
from app.domain.subscriptions.entities.monthly_subscription import MonthlySubscription
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.domain.parking.entities.vehicle import Vehicle

class CreateSubscriptionUseCase:
    """Use case for creating a new monthly subscription"""
    
    def __init__(
        self,
        subscription_repo: ISubscriptionRepository,
        vehicle_repo: IVehicleRepository
    ):
        self.subscription_repo = subscription_repo
        self.vehicle_repo = vehicle_repo
    
    async def execute(
        self,
        plate: str,
        vehicle_type: str,
        owner_name: str,
        owner_phone: str,
        monthly_fee: int,
        start_date: date,
        duration_days: int = 30,
        notes: Optional[str] = None
    ) -> MonthlySubscription:
        # Normalize plate
        plate = plate.upper().strip()
        
        # Check if vehicle exists, if not create it
        vehicle = await self.vehicle_repo.get_by_plate(plate)
        
        if vehicle is None:
            vehicle = Vehicle(
                id=None,
                plate=plate,
                vehicle_type=vehicle_type,
                owner_name=owner_name,
                owner_phone=owner_phone,
                is_frequent=True, # Subscriptions imply frequent customer
                notes=notes
            )
            vehicle = await self.vehicle_repo.create(vehicle)
        else:
            # Update frequent status if not set
            if not vehicle.is_frequent:
                vehicle.is_frequent = True
                await self.vehicle_repo.update(vehicle.id, vehicle)
            
        # Check for active subscription overlap
        # Ideally we should check if there is any subscription that overlaps with the requested period
        # For simplicity, let's just check if there is currently an active one
        active_sub = await self.subscription_repo.get_active_by_vehicle_id(vehicle.id, start_date)
        if active_sub:
             raise ValueError(f"Vehicle {plate} already has an active subscription for the start date")
        
        # Calculate end date
        end_date = start_date + timedelta(days=duration_days)
        
        # Create subscription
        subscription = MonthlySubscription(
            id=None,
            vehicle_id=vehicle.id,
            start_date=start_date,
            end_date=end_date,
            monthly_fee=monthly_fee,
            payment_status="paid", # Assuming paid upfront
            notes=notes
        )
        
        return await self.subscription_repo.create(subscription)
