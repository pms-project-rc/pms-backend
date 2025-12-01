from datetime import datetime
from typing import Optional
from fastapi import HTTPException

from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.parking.repositories.rate_repository import IRateRepository
from app.domain.financial.repositories.shift_repository import ShiftRepository
from app.application.dto.parking.entry_request import EntryRequest
from app.domain.parking.entities.vehicle import Vehicle
from app.domain.parking.entities.parking_record import ParkingRecord

class RegisterEntry:
    def __init__(
        self,
        vehicle_repo: IVehicleRepository,
        parking_repo: IParkingRecordRepository,
        rate_repo: IRateRepository,
        shift_repo: ShiftRepository
    ):
        self.vehicle_repo = vehicle_repo
        self.parking_repo = parking_repo
        self.rate_repo = rate_repo
        self.shift_repo = shift_repo

    async def execute(self, data: EntryRequest, admin_id: int) -> ParkingRecord:
        # 1. Check active shift
        shift = await self.shift_repo.get_active_shift_by_admin(admin_id)
        if not shift:
            raise HTTPException(status_code=400, detail="No active shift found for this admin")

        # 2. Get or Create Vehicle
        vehicle = await self.vehicle_repo.get_by_plate(data.plate)
        if not vehicle:
            vehicle = Vehicle(
                id=None,
                plate=data.plate,
                vehicle_type=data.vehicle_type,
                owner_name=data.owner_name,
                owner_phone=data.owner_phone,
                brand=data.brand,
                model=data.model,
                color=data.color,
                notes=data.notes
            )
            vehicle = await self.vehicle_repo.create(vehicle)
        else:
            # Update vehicle info if needed (optional, but good for keeping data fresh)
            # For now, we assume existing data is correct or we only update if provided
            pass

        # 3. Check if already parked
        active_record = await self.parking_repo.get_active_by_vehicle_id(vehicle.id)
        if active_record:
            raise HTTPException(status_code=400, detail="Vehicle is already parked")

        # 4. Get Rate
        # Assuming rate_type 'Hora' is default for entry, or we logic it out.
        # For now, we get the 'Hora' rate for the vehicle type.
        rate = await self.rate_repo.get_active_by_type(data.vehicle_type, "Hora")
        if not rate:
             # Fallback or error? Let's try 'Dia' if 'Hora' not found, or error.
             # Error is safer.
             raise HTTPException(status_code=400, detail=f"No active rate found for {data.vehicle_type}")

        # 5. Create Record
        record = ParkingRecord(
            id=None,
            vehicle_id=vehicle.id,
            shift_id=shift.id,
            admin_id=admin_id,
            entry_time=datetime.now(),
            parking_rate_id=rate.id,
            helmet_count=data.helmet_count,
            helmet_charge=0, # Calculated on exit or if fixed charge? Usually on exit or fixed.
            # If helmet has a cost, we might need a Rate for helmets too.
            # For now, 0.
            total_cost=0,
            payment_status="pending",
            notes=data.notes
        )
        
        return await self.parking_repo.create(record)
