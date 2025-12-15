from app.domain.agreements.repositories.agreement_repository import IAgreementRepository
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository

class AddVehicleToAgreementUseCase:
    """Use case for adding a vehicle to an agreement"""
    
    def __init__(
        self,
        agreement_repo: IAgreementRepository,
        vehicle_repo: IVehicleRepository
    ):
        self.agreement_repo = agreement_repo
        self.vehicle_repo = vehicle_repo
    
    async def execute(self, agreement_id: int, plate: str, vehicle_type: str = "Automovil"):
        print(f"UseCase: Adding vehicle {plate} (type: {vehicle_type}) to agreement {agreement_id}")
        # Verify agreement exists
        agreement = await self.agreement_repo.get_by_id(agreement_id)
        if not agreement:
            print(f"UseCase: Agreement {agreement_id} not found")
            raise ValueError(f"Agreement with ID {agreement_id} not found")
        
        if agreement.is_active != "active":
            print(f"UseCase: Agreement {agreement_id} is not active")
            raise ValueError(f"Agreement {agreement.company_name} is not active")
        
        # Get vehicle by plate
        plate = plate.upper().strip()
        vehicle = await self.vehicle_repo.get_by_plate(plate)
        
        if not vehicle:
            print(f"UseCase: Vehicle {plate} not found, creating new one")
            # Create vehicle if it doesn't exist
            from app.domain.parking.entities.vehicle import Vehicle
            new_vehicle = Vehicle(
                id=None,
                plate=plate,
                vehicle_type=vehicle_type, 
                owner_name="Convenio", # Placeholder
                owner_phone=None,
                notes="Creado automáticamente desde Convenios"
            )
            try:
                vehicle = await self.vehicle_repo.create(new_vehicle)
                print(f"UseCase: Created vehicle {vehicle.id}")
            except Exception as e:
                print(f"UseCase: Error creating vehicle: {e}")
                raise
        else:
            print(f"UseCase: Vehicle {plate} found (ID: {vehicle.id})")
        
        # Add vehicle to agreement
        try:
            await self.agreement_repo.add_vehicle_to_agreement(agreement_id, vehicle.id)
            print(f"UseCase: Added vehicle {vehicle.id} to agreement {agreement_id}")
        except Exception as e:
            print(f"UseCase: Error adding vehicle to agreement relation: {e}")
            raise
        
        return {"message": f"Vehicle {plate} added to agreement {agreement.company_name}"}
