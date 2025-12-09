from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import date

from app.application.dto.washing.washing_service_dtos import WashingServiceRequest, WashingServiceResponse
from app.application.washing.create_washing_service_use_case import CreateWashingServiceUseCase
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl
from app.infrastructure.repositories.parking.vehicle_repository_impl import VehicleRepositoryImpl
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.api.dependencies.auth import get_current_admin, get_current_washer

router = APIRouter(prefix="", tags=["Washing Services"])

def get_create_washing_service_use_case() -> CreateWashingServiceUseCase:
    washing_repo = WashingServiceRepositoryImpl()
    vehicle_repo = VehicleRepositoryImpl()
    parking_record_repo = ParkingRecordRepositoryImpl()
    return CreateWashingServiceUseCase(washing_repo, vehicle_repo, parking_record_repo)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=WashingServiceResponse)
async def create_washing_service(
    request: WashingServiceRequest,
    current_admin: any = Depends(get_current_admin),
    use_case: CreateWashingServiceUseCase = Depends(get_create_washing_service_use_case)
):
    """
    Register a new washing service.
    """
    try:
        # Get active shift (placeholder logic similar to parking)
        from app.infrastructure.database.session import SessionLocal
        from app.infrastructure.database.models.financial import Shift
        from sqlalchemy import select
        
        async with SessionLocal() as session:
            result = await session.execute(
                select(Shift)
                .where(Shift.admin_id == current_admin.id)
                .where(Shift.shift_date == date.today())
                .where(Shift.end_time.is_(None))
            )
            active_shift = result.scalar_one_or_none()
            
            if not active_shift:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active shift found. Please start a shift first."
                )
            shift_id = active_shift.id

        service = await use_case.execute(
            plate=request.plate,
            vehicle_type=request.vehicle_type,
            service_type=request.service_type,
            price=request.price,
            admin_id=current_admin.id,
            shift_id=shift_id,
            owner_name=request.owner_name,
            owner_phone=request.owner_phone,
            washer_id=request.washer_id,
            notes=request.notes
        )
        
        return WashingServiceResponse(
            id=service.id,
            vehicle_id=service.vehicle_id,
            plate=request.plate,
            service_type=service.service_type,
            price=service.price,
            status=service.payment_status,
            washer_id=service.washer_id,
            service_date=service.service_date
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating washing service: {str(e)}"
        )

@router.get("/active", response_model=List[WashingServiceResponse])
async def list_active_services(
    current_admin: any = Depends(get_current_admin)
):
    """
    List all active washing services.
    """
    try:
        repo = WashingServiceRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl() # To get plate
        
        services = await repo.list_active()
        
        response = []
        for s in services:
            # This is N+1 problem, but acceptable for MVP with low volume
            vehicle = await vehicle_repo.get_by_id(s.vehicle_id)
            plate = vehicle.plate if vehicle else "UNKNOWN"

            response.append(WashingServiceResponse(
                id=s.id,
                vehicle_id=s.vehicle_id,
                plate=plate,
                service_type=s.service_type,
                price=s.price,
                status=s.payment_status,
                washer_id=s.washer_id,
                service_date=s.service_date
            ))
            
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing services: {str(e)}"
        )

@router.get("/my-services", response_model=List[WashingServiceResponse])
async def list_my_services(
    current_washer = Depends(get_current_washer)
):
    """
    List all washing services assigned to the current washer.
    Only returns services where washer_id matches current washer.
    """
    try:
        repo = WashingServiceRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        
        # Obtener solo servicios asignados a este lavador
        services = await repo.list_by_washer(current_washer.id)
        
        response = []
        for s in services:
            # This is N+1 problem, but acceptable for MVP with low volume
            vehicle = await vehicle_repo.get_by_id(s.vehicle_id)
            plate = vehicle.plate if vehicle else "UNKNOWN"

            # Determinar el estado basado en los campos disponibles
            if s.end_time:
                service_status = "completed"
            elif s.start_time:
                service_status = "in_progress"
            else:
                service_status = "pending"

            response.append(WashingServiceResponse(
                id=s.id,
                vehicle_id=s.vehicle_id,
                plate=plate,
                service_type=s.service_type,
                price=s.price,
                status=service_status,  # Usar el estado calculado
                washer_id=s.washer_id,
                service_date=s.service_date,
                start_time=s.start_time,
                end_time=s.end_time
            ))
            
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing washer services: {str(e)}"
        )

@router.put("/{service_id}/assign/{washer_id}", response_model=WashingServiceResponse)
async def assign_washer(
    service_id: int,
    washer_id: int,
    current_admin: any = Depends(get_current_admin)
):
    """
    Assign a washer to a service.
    """
    try:
        from app.application.washing.assign_washer_use_case import AssignWasherUseCase
        from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
        
        washing_repo = WashingServiceRepositoryImpl()
        washer_repo = WasherRepositoryImpl()
        use_case = AssignWasherUseCase(washing_repo, washer_repo)
        
        service = await use_case.execute(service_id, washer_id)
        
        # Get plate for response
        vehicle_repo = VehicleRepositoryImpl()
        vehicle = await vehicle_repo.get_by_id(service.vehicle_id)
        plate = vehicle.plate if vehicle else "UNKNOWN"
        
        return WashingServiceResponse(
            id=service.id,
            vehicle_id=service.vehicle_id,
            plate=plate,
            service_type=service.service_type,
            price=service.price,
            status=service.payment_status,
            washer_id=service.washer_id,
            service_date=service.service_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error assigning washer: {str(e)}"
        )

@router.put("/{service_id}/complete", response_model=WashingServiceResponse)
async def complete_service(
    service_id: int,
    current_admin: any = Depends(get_current_admin)
):
    """
    Mark a washing service as completed and paid.
    """
    try:
        from app.application.washing.complete_washing_service_use_case import CompleteWashingServiceUseCase
        
        washing_repo = WashingServiceRepositoryImpl()
        use_case = CompleteWashingServiceUseCase(washing_repo)
        
        service = await use_case.execute(service_id)
        
        # Get plate for response
        vehicle_repo = VehicleRepositoryImpl()
        vehicle = await vehicle_repo.get_by_id(service.vehicle_id)
        plate = vehicle.plate if vehicle else "UNKNOWN"
        
        return WashingServiceResponse(
            id=service.id,
            vehicle_id=service.vehicle_id,
            plate=plate,
            service_type=service.service_type,
            price=service.price,
            status=service.payment_status,
            washer_id=service.washer_id,
            service_date=service.service_date
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error completing service: {str(e)}"
        )
