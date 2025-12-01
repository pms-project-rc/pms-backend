from datetime import datetime, timezone, date
from typing import Optional
from app.domain.parking.entities.parking_record import ParkingRecord
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.core.washing_config import WashingServiceConfig
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.parking.repositories.rate_repository import IRateRepository
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository
from app.domain.agreements.repositories.agreement_repository import IAgreementRepository
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository


class VehicleExitUseCase:
    """Use case for registering vehicle exit from parking"""
    
    def __init__(
        self,
        vehicle_repo: IVehicleRepository,
        parking_record_repo: IParkingRecordRepository,
        rate_repo: IRateRepository,
        subscription_repo: ISubscriptionRepository,
        agreement_repo: IAgreementRepository,
        washing_repo: IWashingServiceRepository
    ):
        self.vehicle_repo = vehicle_repo
        self.parking_record_repo = parking_record_repo
        self.rate_repo = rate_repo
        self.subscription_repo = subscription_repo
        self.agreement_repo = agreement_repo
        self.washing_repo = washing_repo
    
    async def execute(
        self,
        plate: str,
        notes: Optional[str] = None
    ) -> ParkingRecord:
        """
        Register a vehicle exit from the parking lot and calculate the total cost.
        
        Pricing logic:
        1. If vehicle has active subscription: parking cost = 0 (only charge helmets)
        2. If washing service linked: apply free parking minutes
        3. If vehicle has agreement: apply discount or special rate
        4. Otherwise: apply standard hourly rate
        
        Args:
            plate: Vehicle license plate
            notes: Optional notes for the exit
            
        Returns:
            Updated ParkingRecord with exit time and total cost
            
        Raises:
            ValueError: If vehicle not found or no active parking record
        """
        # Normalize plate to uppercase
        plate = plate.upper().strip()
        
        # Find vehicle
        vehicle = await self.vehicle_repo.get_by_plate(plate)
        if not vehicle:
            raise ValueError(f"Vehicle with plate {plate} not found")
        
        # Find active parking record
        parking_record = await self.parking_record_repo.get_active_by_vehicle_id(vehicle.id)
        if not parking_record:
            raise ValueError(f"No active parking record found for vehicle {plate}")
        
        # Set exit time
        exit_time = datetime.now(timezone.utc)
        parking_record.exit_time = exit_time
        
        # Calculate parking duration in minutes
        duration = exit_time - parking_record.entry_time
        minutes_total = duration.total_seconds() / 60
        
        # Check for free parking minutes from washing service
        free_minutes = 0
        if parking_record.washing_service_id:
            washing_service = await self.washing_repo.get_by_id(parking_record.washing_service_id)
            if washing_service:
                # Get free minutes from config
                free_minutes = WashingServiceConfig.get_free_minutes(
                    vehicle.vehicle_type,
                    washing_service.service_type
                )
        
        # Apply free minutes
        billable_minutes = max(0, minutes_total - free_minutes)
        
        # Convert to hours (rounded up)
        import math
        hours_rounded = max(1, math.ceil(billable_minutes / 60))
        
        # If billable minutes is 0 (covered by free time), cost should be 0?
        # Rule: "La tarifa mínima es de 1 minuto." -> If billable > 0, min 1 hour charge usually.
        # But if fully covered by free time, it should be 0.
        if billable_minutes == 0:
            hours_rounded = 0
        
        # Initialize parking cost
        parking_cost = 0
        
        # Check if vehicle has active subscription
        if parking_record.subscription_id:
            # Subscription: parking is free, only charge helmets
            parking_cost = 0
        else:
            # No subscription: check for agreement or apply standard rate
            agreement = await self.agreement_repo.get_agreement_by_vehicle_id(vehicle.id)
            
            if agreement and agreement.is_active == "active":
                # Has active agreement
                if agreement.special_rate:
                    # Use special rate (fixed rate per hour)
                    parking_cost = agreement.special_rate * hours_rounded
                else:
                    # Apply discount percentage to standard rate
                    rate = await self.rate_repo.get_by_id(parking_record.parking_rate_id)
                    if not rate:
                        raise ValueError(f"Rate not found for parking record")
                    
                    standard_cost = rate.price * hours_rounded
                    discount = standard_cost * (agreement.discount_percentage / 100)
                    parking_cost = standard_cost - discount
            else:
                # No agreement: use standard rate
                rate = await self.rate_repo.get_by_id(parking_record.parking_rate_id)
                if not rate:
                    raise ValueError(f"Rate not found for parking record")
                
                parking_cost = rate.price * hours_rounded
        
        # Calculate total cost (parking + helmet charge)
        total_cost = int(parking_cost) + parking_record.helmet_charge
        
        parking_record.total_cost = total_cost
        parking_record.payment_status = "paid"  # Assuming immediate payment
        
        if notes:
            parking_record.notes = notes
        
        # Update parking record
        updated_record = await self.parking_record_repo.update(
            parking_record.id,
            parking_record
        )
        
        return updated_record
