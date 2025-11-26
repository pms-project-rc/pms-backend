"""
Parking API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.database import get_db
from app.application.dto.parking.parking_request import ParkingEntryRequest
from app.application.dto.parking.parking_response import (
    ActiveParkingItem,
    ActiveParkingResponse,
    ParkingEntryResponse,
    VehicleInfo,
)
from app.application.parking.register_parking_entry import (
    GetActiveParkingUseCase,
    RegisterParkingEntryUseCase,
)
from app.infrastructure.repositories.sqlalchemy_parking_repository import (
    SQLAlchemyParkingRepository,
)
from app.infrastructure.repositories.sqlalchemy_rate_repository import (
    SQLAlchemyRateRepository,
)
from app.infrastructure.repositories.sqlalchemy_vehicle_repository import (
    SQLAlchemyVehicleRepository,
)

router = APIRouter(prefix="/parking", tags=["Parking"])


@router.post(
    "/entry",
    response_model=ParkingEntryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register parking entry",
    description="Register a vehicle entry into the parking lot with automatic classification and helmet charge calculation",
)
async def register_parking_entry(
    request: ParkingEntryRequest,
    db: AsyncSession = Depends(get_db),
) -> ParkingEntryResponse:
    """
    Register a vehicle entry into the parking lot (HU-07).
    
    Business Rules:
    - Automatically classifies vehicle type based on plate format
    - Plates ending in LETTER → Motorcycle
    - Plates ending in NUMBER → Car
    - Calculates helmet charges for motorcycles ($1,000 COP per helmet)
    - Prevents duplicate entries for vehicles already parked
    
    Args:
        request: Parking entry request data
        db: Database session
        
    Returns:
        ParkingEntryResponse: Created parking record details
        
    Raises:
        HTTPException 400: Invalid input data
        HTTPException 409: Vehicle already parked
        HTTPException 500: Server error
    """
    try:
        # Initialize repositories
        parking_repo = SQLAlchemyParkingRepository(db)
        vehicle_repo = SQLAlchemyVehicleRepository(db)
        rate_repo = SQLAlchemyRateRepository(db)
        
        # Execute use case
        use_case = RegisterParkingEntryUseCase(
            parking_repo=parking_repo,
            vehicle_repo=vehicle_repo,
            rate_repo=rate_repo,
        )
        
        result = await use_case.execute(
            plate=request.plate,
            helmet_count=request.helmet_count,
            owner_name=request.owner_name,
            owner_phone=request.owner_phone,
            notes=request.notes,
        )
        
        # Commit transaction
        await db.commit()
        
        # Build response
        return ParkingEntryResponse(
            parking_id=result["parking_id"],
            vehicle=VehicleInfo(
                id=result["vehicle_id"],
                plate=result["plate"],
                vehicle_type=result["vehicle_type"],
                owner_name=result["owner_name"],
                owner_phone=result["owner_phone"],
            ),
            entry_time=result["entry_time"],
            helmet_count=result["helmet_count"],
            helmet_charge=result["helmet_charge"],
            total_cost=result["total_cost"],
            payment_status=result["payment_status"],
            message="Vehículo registrado exitosamente en el parqueadero",
        )
        
    except ValueError as e:
        # Business rule violation or validation error
        await db.rollback()
        
        # Check if it's a duplicate entry error
        if "ya se encuentra en el parqueadero" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(e),
            )
        
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    
    except Exception as e:
        # Unexpected error
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al registrar el ingreso al parqueadero: {str(e)}",
        )


@router.get(
    "/active",
    response_model=ActiveParkingResponse,
    summary="Get active parking records",
    description="Retrieve all vehicles currently parked (not yet exited)",
)
async def get_active_parking(
    db: AsyncSession = Depends(get_db),
) -> ActiveParkingResponse:
    """
    Get all active parking records.
    
    Returns all vehicles currently in the parking lot (no exit time registered).
    
    Args:
        db: Database session
        
    Returns:
        ActiveParkingResponse: List of active parking records
    """
    try:
        # Initialize repositories
        parking_repo = SQLAlchemyParkingRepository(db)
        vehicle_repo = SQLAlchemyVehicleRepository(db)
        
        # Execute use case
        use_case = GetActiveParkingUseCase(
            parking_repo=parking_repo,
            vehicle_repo=vehicle_repo,
        )
        
        records = await use_case.execute()
        
        # Build response
        vehicles = [
            ActiveParkingItem(
                parking_id=record["parking_id"],
                vehicle_plate=record.get("plate", "N/A"),
                vehicle_type=record.get("vehicle_type", "UNKNOWN"),
                entry_time=record["entry_time"],
                helmet_count=record["helmet_count"],
                total_cost=record["total_cost"],
            )
            for record in records
        ]
        
        return ActiveParkingResponse(
            count=len(vehicles),
            vehicles=vehicles,
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener vehículos parqueados: {str(e)}",
        )


@router.get(
    "/{parking_id}",
    summary="Get parking record details",
    description="Retrieve detailed information about a specific parking record",
)
async def get_parking_record(
    parking_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get parking record by ID.
    
    Args:
        parking_id: ID of the parking record
        db: Database session
        
    Returns:
        Parking record details
        
    Raises:
        HTTPException 404: Parking record not found
    """
    try:
        parking_repo = SQLAlchemyParkingRepository(db)
        record = await parking_repo.get_by_id(parking_id)
        
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Registro de parqueo con ID {parking_id} no encontrado",
            )
        
        return record
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener el registro de parqueo: {str(e)}",
        )
