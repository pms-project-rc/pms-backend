from datetime import datetime
from typing import Optional
from fastapi import HTTPException
import math

from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.parking.repositories.rate_repository import IRateRepository
from app.application.dto.parking.exit_request import ExitRequest
from app.domain.parking.entities.parking_record import ParkingRecord

class RegisterExit:
    def __init__(
        self,
        vehicle_repo: IVehicleRepository,
        parking_repo: IParkingRecordRepository,
        rate_repo: IRateRepository
    ):
        self.vehicle_repo = vehicle_repo
        self.parking_repo = parking_repo
        self.rate_repo = rate_repo

    async def execute(self, data: ExitRequest) -> ParkingRecord:
        # 1. Get Vehicle
        vehicle = await self.vehicle_repo.get_by_plate(data.plate)
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # 2. Get Active Record
        record = await self.parking_repo.get_active_by_vehicle_id(vehicle.id)
        if not record:
            raise HTTPException(status_code=400, detail="Vehicle is not parked")

        # 3. Calculate Cost
        rate = await self.rate_repo.get_by_id(record.parking_rate_id)
        if not rate:
             raise HTTPException(status_code=500, detail="Rate not found")

        exit_time = datetime.now()
        duration = exit_time - record.entry_time.replace(tzinfo=None) # Ensure naive/aware compatibility
        # Assuming entry_time is timezone aware or naive depending on DB. 
        # Postgres returns aware if timezone=True. datetime.now() is naive.
        # Let's use datetime.utcnow() or proper timezone handling.
        # For simplicity, let's assume naive for now or handle it.
        # Best to use aware everywhere.
        
        # If record.entry_time is aware, we need aware now.
        if record.entry_time.tzinfo:
            from datetime import timezone
            exit_time = datetime.now(timezone.utc)
        
        duration = exit_time - record.entry_time
        hours = math.ceil(duration.total_seconds() / 3600)
        if hours < 1:
            hours = 1
            
        total_cost = hours * rate.price
        
        # Add helmet charge if any
        total_cost += record.helmet_charge

        # 4. Update Record
        record.exit_time = exit_time
        record.total_cost = total_cost
        record.payment_status = "paid" # Or pending if payment is separate
        if data.notes:
            record.notes = data.notes
            
        return await self.parking_repo.update(record.id, record)
