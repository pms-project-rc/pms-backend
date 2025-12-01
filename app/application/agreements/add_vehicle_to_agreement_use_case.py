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
    
    async def execute(self, agreement_id: int, plate: str):
        # Verify agreement exists
        agreement = await self.agreement_repo.get_by_id(agreement_id)
        if not agreement:
            raise ValueError(f"Agreement with ID {agreement_id} not found")
        
        if agreement.is_active != "active":
            raise ValueError(f"Agreement {agreement.company_name} is not active")
        
        # Get vehicle by plate
        plate = plate.upper().strip()
        vehicle = await self.vehicle_repo.get_by_plate(plate)
        
        if not vehicle:
            raise ValueError(f"Vehicle with plate {plate} not found")
        
        # Add vehicle to agreement
        await self.agreement_repo.add_vehicle_to_agreement(agreement_id, vehicle.id)
        
        return {"message": f"Vehicle {plate} added to agreement {agreement.company_name}"}
