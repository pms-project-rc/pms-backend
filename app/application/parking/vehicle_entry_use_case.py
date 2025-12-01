from datetime import datetime, timezone
from typing import Optional
from app.domain.parking.entities.vehicle import Vehicle
from app.domain.parking.entities.parking_record import ParkingRecord
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.parking.repositories.rate_repository import IRateRepository
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository

class VehicleEntryUseCase:
    """Use case for registering vehicle entry to parking"""
    
    def __init__(
        self,
        vehicle_repo: IVehicleRepository,
        parking_record_repo: IParkingRecordRepository,
        rate_repo: IRateRepository,
        subscription_repo: ISubscriptionRepository
    ):
        self.vehicle_repo = vehicle_repo
        self.parking_record_repo = parking_record_repo
        self.rate_repo = rate_repo
        self.subscription_repo = subscription_repo
    
    async def execute(
        self,
        plate: str,
        vehicle_type: str,
        owner_name: str,
        shift_id: int,
        admin_id: int,
        owner_phone: Optional[str] = None,
        brand: Optional[str] = None,
        model: Optional[str] = None,
        color: Optional[str] = None,
        notes: Optional[str] = None,
        helmet_count: int = 0
    ) -> ParkingRecord:
        # ... (previous code for normalization and vehicle creation/check) ...
        # Normalize plate to uppercase and vehicle_type to lowercase
        plate = plate.upper().strip()
        vehicle_type = vehicle_type.lower().strip()
        
        # Check if vehicle exists, if not create it
        vehicle = await self.vehicle_repo.get_by_plate(plate)
        
        if vehicle is None:
            # Create new vehicle
            vehicle = Vehicle(
                id=None,
                plate=plate,
                vehicle_type=vehicle_type,
                owner_name=owner_name,
                owner_phone=owner_phone,
                brand=brand,
                model=model,
                color=color,
                is_frequent=False,
                notes=notes
            )
            vehicle = await self.vehicle_repo.create(vehicle)
        else:
            # Check if vehicle already has an active parking record
            active_record = await self.parking_record_repo.get_active_by_vehicle_id(vehicle.id)
            if active_record:
                raise ValueError(f"Vehicle {plate} already has an active parking record")
        
        # Check for active subscription
        from datetime import date
        active_subscription = await self.subscription_repo.get_active_by_vehicle_id(vehicle.id, date.today())
        subscription_id = active_subscription.id if active_subscription else None

        # Get the appropriate rate for this vehicle type
        # Default to "hour" (hourly) rate type
        rate = await self.rate_repo.get_active_by_type(vehicle_type, "hour")
        if not rate:
            raise ValueError(f"No active rate found for vehicle type: {vehicle_type}")
        
        # Calculate helmet charge if applicable
        helmet_charge = 0
        if helmet_count > 0:
            # Helmet charge: 1000 pesos (100000 centavos) per helmet
            helmet_charge = helmet_count * 100000
        
        # Create parking record
        parking_record = ParkingRecord(
            id=None,
            vehicle_id=vehicle.id,
            shift_id=shift_id,
            admin_id=admin_id,
            entry_time=datetime.now(timezone.utc),
            parking_rate_id=rate.id,
            exit_time=None,
            subscription_id=subscription_id,
            washing_service_id=None,
            helmet_count=helmet_count,
            helmet_charge=helmet_charge,
            total_cost=0,  # Will be calculated on exit
            payment_status="pending",
            notes=notes
        )
        
        # Save parking record
        parking_record = await self.parking_record_repo.create(parking_record)
        
        return parking_record
