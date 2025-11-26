"""
Use case for registering parking entry.
"""
from datetime import datetime
from typing import Optional

from app.domain.parking.entities.parking_entry import ParkingEntry
from app.domain.parking.repositories.parking_repository import IParkingRepository
from app.domain.parking.repositories.rate_repository import IRateRepository
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository
from app.domain.parking.value_objects.vehicle_plate import VehiclePlate
from app.domain.parking.value_objects.vehicle_type import VehicleType


class RegisterParkingEntryUseCase:
    """
    Use case for registering a vehicle entry into the parking lot.
    
    Implements business logic for HU-07:
    1. Validate input
    2. Classify vehicle type from plate
    3. Find or create vehicle record
    4. Check if vehicle is already parked
    5. Get applicable parking rate
    6. Calculate helmet charges
    7. Create parking record
    """
    
    def __init__(
        self,
        parking_repo: IParkingRepository,
        vehicle_repo: IVehicleRepository,
        rate_repo: IRateRepository,
    ):
        self.parking_repo = parking_repo
        self.vehicle_repo = vehicle_repo
        self.rate_repo = rate_repo
    
    async def execute(
        self,
        plate: str,
        helmet_count: int = 0,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> dict:
        """
        Execute the parking entry registration use case.
        
        Args:
            plate: Vehicle license plate
            helmet_count: Number of helmets (for motorcycles)
            owner_name: Vehicle owner name
            owner_phone: Vehicle owner phone
            notes: Additional notes
            
        Returns:
            dict: Parking entry result with vehicle and parking info
            
        Raises:
            ValueError: If validation fails or vehicle is already parked
        """
        # Step 1: Create and validate plate
        vehicle_plate = VehiclePlate(plate)
        
        # Step 2: Auto-classify vehicle type from plate
        classified_type = vehicle_plate.classified_vehicle_type
        
        # Step 3: Find or create vehicle record
        vehicle_data = await self.vehicle_repo.find_by_plate(vehicle_plate)
        
        if vehicle_data:
            vehicle_id = vehicle_data["id"]
            vehicle_type = VehicleType(vehicle_data["vehicle_type"])
            
            # Update owner info if provided and different
            if owner_name and owner_name != vehicle_data.get("owner_name"):
                await self.vehicle_repo.update_vehicle(
                    vehicle_id=vehicle_id,
                    owner_name=owner_name,
                    owner_phone=owner_phone,
                )
        else:
            # Create new vehicle with classified type
            vehicle_id = await self.vehicle_repo.create_vehicle(
                plate=vehicle_plate,
                vehicle_type=classified_type,
                owner_name=owner_name,
                owner_phone=owner_phone,
            )
            vehicle_type = classified_type
        
        # Step 4: Check if vehicle is already parked
        active_parking = await self.parking_repo.find_active_by_vehicle(vehicle_id)
        if active_parking:
            raise ValueError(
                f"El vehículo con placa {plate} ya se encuentra en el parqueadero. "
                f"Debe registrar su salida antes de un nuevo ingreso."
            )
        
        # Step 5: Get applicable parking rate
        rate_data = await self.rate_repo.find_active_rate(
            vehicle_type=vehicle_type,
            rate_type="Hora"
        )
        
        if not rate_data:
            # Fallback to default rate
            rate_data = await self.rate_repo.get_default_rate()
            
        if not rate_data:
            raise ValueError(
                "No se encontró una tarifa activa para este tipo de vehículo. "
                "Por favor, configure las tarifas en el sistema."
            )
        
        rate_id = rate_data["id"]
        
        # Step 6: Create parking entry domain entity
        entry_time = datetime.now()
        
        parking_entry = ParkingEntry(
            plate=vehicle_plate,
            entry_time=entry_time,
            vehicle_type=vehicle_type,
            helmet_count=helmet_count,
            owner_name=owner_name,
            owner_phone=owner_phone,
            notes=notes,
            helmet_unit_price=rate_data.get("helmet_fee", 0),
        )
        
        # Step 7: Create parking record
        parking_id = await self.parking_repo.create_parking_entry(
            entry=parking_entry,
            vehicle_id=vehicle_id,
            rate_id=rate_id,
        )
        
        # Step 8: Return success result
        return {
            "parking_id": parking_id,
            "vehicle_id": vehicle_id,
            "plate": str(vehicle_plate),
            "vehicle_type": vehicle_type.value,
            "entry_time": entry_time,
            "helmet_count": parking_entry.helmet_count,
            "helmet_charge": parking_entry.helmet_charge,
            "total_cost": parking_entry.helmet_charge,
            "payment_status": "pending",
            "owner_name": owner_name or "Desconocido",
            "owner_phone": owner_phone,
        }


class GetActiveParkingUseCase:
    """
    Use case for retrieving all active parking records.
    """
    
    def __init__(
        self,
        parking_repo: IParkingRepository,
        vehicle_repo: IVehicleRepository,
    ):
        self.parking_repo = parking_repo
        self.vehicle_repo = vehicle_repo
    
    async def execute(self) -> list[dict]:
        """
        Get all active parking records with vehicle information.
        
        Returns:
            list[dict]: List of active parking records
        """
        active_records = await self.parking_repo.get_all_active()
        
        # Enrich with vehicle information
        result = []
        for record in active_records:
            vehicle_data = await self.vehicle_repo.find_by_plate(
                VehiclePlate(record.get("plate", ""))
            ) if "plate" in record else None
            
            result.append({
                "parking_id": record["id"],
                "vehicle_id": record["vehicle_id"],
                "entry_time": record["entry_time"],
                "helmet_count": record.get("helmet_count", 0),
                "helmet_charge": record.get("helmet_charge", 0),
                "total_cost": record["total_cost"],
                "payment_status": record["payment_status"],
            })
        
        return result
