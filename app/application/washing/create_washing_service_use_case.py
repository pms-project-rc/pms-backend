from datetime import datetime, timezone
from typing import Optional
from app.domain.washing.entities.washing_service import WashingService
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.parking.entities.vehicle import Vehicle

class CreateWashingServiceUseCase:
    """Use case for registering a new washing service"""
    
    def __init__(
        self,
        washing_repo: IWashingServiceRepository,
        vehicle_repo: IVehicleRepository,
        parking_record_repo: IParkingRecordRepository
    ):
        self.washing_repo = washing_repo
        self.vehicle_repo = vehicle_repo
        self.parking_record_repo = parking_record_repo
    
    async def execute(
        self,
        plate: str,
        vehicle_type: str,
        service_type: str,
        price: int,
        admin_id: int,
        shift_id: int,
        owner_name: str,
        owner_phone: Optional[str] = None,
        washer_id: Optional[int] = None,
        notes: Optional[str] = None
    ) -> WashingService:
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
                is_frequent=False,
                notes=notes
            )
            vehicle = await self.vehicle_repo.create(vehicle)
            
        # Check for active parking record to associate
        active_record = await self.parking_record_repo.get_active_by_vehicle_id(vehicle.id)
        parking_record_id = active_record.id if active_record else None
        
        # Create washing service
        service = WashingService(
            id=None,
            vehicle_id=vehicle.id,
            shift_id=shift_id,
            admin_id=admin_id,
            service_type=service_type,
            service_date=datetime.now(timezone.utc),
            price=price,
            parking_record_id=parking_record_id,
            washer_id=washer_id,
            start_time=None, # Will be set when washer starts
            end_time=None,
            payment_status="pending",
            notes=notes
        )
        
        created_service = await self.washing_repo.create(service)
        
        # Update parking record to link to this washing service
        if active_record:
            active_record.washing_service_id = created_service.id
            await self.parking_record_repo.update(active_record.id, active_record)
        
        return created_service
