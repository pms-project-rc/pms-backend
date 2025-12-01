from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.application.dto.agreements.agreement_dtos import AgreementRequest, AgreementResponse, AddVehicleRequest
from app.application.agreements.create_agreement_use_case import CreateAgreementUseCase
from app.application.agreements.add_vehicle_to_agreement_use_case import AddVehicleToAgreementUseCase
from app.infrastructure.repositories.agreements.agreement_repository_impl import AgreementRepositoryImpl
from app.infrastructure.repositories.parking.vehicle_repository_impl import VehicleRepositoryImpl
from app.api.dependencies.auth import get_current_operational_admin
from app.infrastructure.database.models.users import OperationalAdmin

router = APIRouter(prefix="/agreements", tags=["Agreements"])

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AgreementResponse)
async def create_agreement(
    request: AgreementRequest,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Create a new company agreement.
    """
    try:
        agreement_repo = AgreementRepositoryImpl()
        use_case = CreateAgreementUseCase(agreement_repo)
        
        agreement = await use_case.execute(
            company_name=request.company_name,
            contact_name=request.contact_name,
            start_date=request.start_date,
            discount_percentage=request.discount_percentage,
            contact_phone=request.contact_phone,
            contact_email=request.contact_email,
            end_date=request.end_date,
            special_rate=request.special_rate,
            notes=request.notes
        )
        
        return AgreementResponse(
            id=agreement.id,
            company_name=agreement.company_name,
            contact_name=agreement.contact_name,
            contact_phone=agreement.contact_phone,
            contact_email=agreement.contact_email,
            start_date=agreement.start_date,
            end_date=agreement.end_date,
            discount_percentage=agreement.discount_percentage,
            special_rate=agreement.special_rate,
            is_active=agreement.is_active,
            notes=agreement.notes
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating agreement: {str(e)}"
        )

@router.get("/", response_model=List[AgreementResponse])
async def list_agreements(
    active_only: bool = False,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    List all agreements or only active ones.
    """
    try:
        agreement_repo = AgreementRepositoryImpl()
        
        if active_only:
            agreements = await agreement_repo.list_active()
        else:
            agreements = await agreement_repo.list_all()
        
        return [
            AgreementResponse(
                id=a.id,
                company_name=a.company_name,
                contact_name=a.contact_name,
                contact_phone=a.contact_phone,
                contact_email=a.contact_email,
                start_date=a.start_date,
                end_date=a.end_date,
                discount_percentage=a.discount_percentage,
                special_rate=a.special_rate,
                is_active=a.is_active,
                notes=a.notes
            )
            for a in agreements
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing agreements: {str(e)}"
        )

@router.get("/{agreement_id}", response_model=AgreementResponse)
async def get_agreement(
    agreement_id: int,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Get agreement by ID.
    """
    try:
        agreement_repo = AgreementRepositoryImpl()
        agreement = await agreement_repo.get_by_id(agreement_id)
        
        if not agreement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agreement with ID {agreement_id} not found"
            )
        
        return AgreementResponse(
            id=agreement.id,
            company_name=agreement.company_name,
            contact_name=agreement.contact_name,
            contact_phone=agreement.contact_phone,
            contact_email=agreement.contact_email,
            start_date=agreement.start_date,
            end_date=agreement.end_date,
            discount_percentage=agreement.discount_percentage,
            special_rate=agreement.special_rate,
            is_active=agreement.is_active,
            notes=agreement.notes
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting agreement: {str(e)}"
        )

@router.post("/{agreement_id}/vehicles", status_code=status.HTTP_201_CREATED)
async def add_vehicle_to_agreement(
    agreement_id: int,
    request: AddVehicleRequest,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Add a vehicle to an agreement.
    """
    try:
        agreement_repo = AgreementRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        use_case = AddVehicleToAgreementUseCase(agreement_repo, vehicle_repo)
        
        result = await use_case.execute(agreement_id, request.plate)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding vehicle to agreement: {str(e)}"
        )

@router.delete("/{agreement_id}/vehicles/{plate}", status_code=status.HTTP_200_OK)
async def remove_vehicle_from_agreement(
    agreement_id: int,
    plate: str,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Remove a vehicle from an agreement.
    """
    try:
        agreement_repo = AgreementRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        
        plate = plate.upper().strip()
        vehicle = await vehicle_repo.get_by_plate(plate)
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with plate {plate} not found"
            )
        
        await agreement_repo.remove_vehicle_from_agreement(agreement_id, vehicle.id)
        
        return {"message": f"Vehicle {plate} removed from agreement"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing vehicle from agreement: {str(e)}"
        )
