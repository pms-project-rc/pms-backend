from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.application.dto.parking.entry_request import EntryRequest
from app.application.dto.parking.exit_request import ExitRequest
from app.application.parking.vehicle_entry_use_case import VehicleEntryUseCase
from app.application.parking.vehicle_exit_use_case import VehicleExitUseCase
from app.infrastructure.repositories.parking.vehicle_repository_impl import VehicleRepositoryImpl
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.infrastructure.repositories.parking.rate_repository_impl import RateRepositoryImpl
from app.api.dependencies.auth import get_current_operational_admin
from app.infrastructure.database.models.users import OperationalAdmin

router = APIRouter(prefix="/parking", tags=["Parking"])


from app.infrastructure.repositories.subscriptions.subscription_repository_impl import SubscriptionRepositoryImpl
from app.infrastructure.repositories.agreements.agreement_repository_impl import AgreementRepositoryImpl
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl

# Dependency to get repositories and use cases
def get_vehicle_entry_use_case() -> VehicleEntryUseCase:
    vehicle_repo = VehicleRepositoryImpl()
    parking_record_repo = ParkingRecordRepositoryImpl()
    rate_repo = RateRepositoryImpl()
    subscription_repo = SubscriptionRepositoryImpl()
    return VehicleEntryUseCase(vehicle_repo, parking_record_repo, rate_repo, subscription_repo)


def get_vehicle_exit_use_case() -> VehicleExitUseCase:
    vehicle_repo = VehicleRepositoryImpl()
    parking_record_repo = ParkingRecordRepositoryImpl()
    rate_repo = RateRepositoryImpl()
    subscription_repo = SubscriptionRepositoryImpl()
    agreement_repo = AgreementRepositoryImpl()
    washing_repo = WashingServiceRepositoryImpl()
    return VehicleExitUseCase(
        vehicle_repo,
        parking_record_repo,
        rate_repo,
        subscription_repo,
        agreement_repo,
        washing_repo
    )


@router.post("/entry", status_code=status.HTTP_201_CREATED)
async def register_entry(
    request: EntryRequest,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin),
    use_case: VehicleEntryUseCase = Depends(get_vehicle_entry_use_case)
):
    """
    Register a vehicle entry to the parking lot.
    
    - **plate**: Vehicle license plate (required)
    - **vehicle_type**: Type of vehicle - Moto, Carro, etc. (required)
    - **owner_name**: Name of the vehicle owner (required)
    - **owner_phone**: Phone number (optional)
    - **brand**: Vehicle brand (optional)
    - **model**: Vehicle model (optional)
    - **color**: Vehicle color (optional)
    - **notes**: Additional notes (optional)
    - **helmet_count**: Number of helmets for motorcycles (default: 0)
    """
    try:
        # Get the current active shift for this admin
        from app.infrastructure.database.session import SessionLocal
        from app.infrastructure.database.models.financial import Shift
        from sqlalchemy import select
        from datetime import date
        
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
                    detail="No active shift found for current admin. Please start a shift first."
                )
            
            shift_id = active_shift.id
        
        parking_record = await use_case.execute(
            plate=request.plate,
            vehicle_type=request.vehicle_type,
            owner_name=request.owner_name,
            shift_id=shift_id,
            admin_id=current_admin.id,
            owner_phone=request.owner_phone,
            brand=request.brand,
            model=request.model,
            color=request.color,
            notes=request.notes,
            helmet_count=request.helmet_count
        )
        
        return {
            "message": "Vehicle entry registered successfully",
            "parking_record_id": parking_record.id,
            "vehicle_id": parking_record.vehicle_id,
            "entry_time": parking_record.entry_time.isoformat(),
            "helmet_count": parking_record.helmet_count,
            "helmet_charge": parking_record.helmet_charge,
            "plate": request.plate
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering vehicle entry: {str(e)}"
        )


@router.post("/exit", status_code=status.HTTP_200_OK)
async def register_exit(
    request: ExitRequest,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin),
    use_case: VehicleExitUseCase = Depends(get_vehicle_exit_use_case)
):
    """
    Register a vehicle exit from the parking lot and calculate the total cost.
    
    - **plate**: Vehicle license plate (required)
    - **notes**: Additional notes (optional)
    """
    try:
        parking_record = await use_case.execute(
            plate=request.plate,
            notes=request.notes
        )
        
        # Calculate duration
        duration = parking_record.exit_time - parking_record.entry_time
        hours = duration.total_seconds() / 3600
        
        return {
            "message": "Vehicle exit registered successfully",
            "parking_record_id": parking_record.id,
            "plate": request.plate,
            "entry_time": parking_record.entry_time.isoformat(),
            "exit_time": parking_record.exit_time.isoformat(),
            "duration_hours": round(hours, 2),
            "helmet_charge": parking_record.helmet_charge,
            "total_cost": parking_record.total_cost,
            "payment_status": parking_record.payment_status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering vehicle exit: {str(e)}"
        )


@router.get("/active", status_code=status.HTTP_200_OK)
async def list_active_vehicles(
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    List all vehicles currently parked (active parking records) with detailed information.
    """
    try:
        from app.infrastructure.database.session import SessionLocal
        from app.infrastructure.database.models.vehicles import ParkingRecord as ParkingRecordModel, Vehicle as VehicleModel
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        
        async with SessionLocal() as session:
            result = await session.execute(
                select(ParkingRecordModel)
                .options(joinedload(ParkingRecordModel.vehicle))
                .where(ParkingRecordModel.exit_time.is_(None))
                .order_by(ParkingRecordModel.entry_time.desc())
            )
            active_records = result.scalars().all()
            
            records_data = []
            for record in active_records:
                # Calculate duration so far
                from datetime import timezone
                now = datetime.now(timezone.utc)
                duration = now - record.entry_time
                hours = int(duration.total_seconds() // 3600)
                minutes = int((duration.total_seconds() % 3600) // 60)
                duration_str = f"{hours}h {minutes}m"
                
                records_data.append({
                    "id": record.id,
                    "vehicle_id": record.vehicle_id,
                    "plate": record.vehicle.plate,
                    "vehicle_type": record.vehicle.vehicle_type,
                    "owner_name": record.vehicle.owner_name,
                    "owner_phone": record.vehicle.owner_phone,
                    "brand": record.vehicle.brand,
                    "model": record.vehicle.model,
                    "color": record.vehicle.color,
                    "entry_time": record.entry_time.isoformat(),
                    "helmet_count": record.helmet_count,
                    "helmet_charge": record.helmet_charge,
                    "notes": record.notes,
                    "duration_so_far": duration_str
                })
            
            return {
                "message": "Active parking records retrieved successfully",
                "count": len(records_data),
                "records": records_data
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving active parking records: {str(e)}"
        )


@router.get("/vehicle/{plate}", status_code=status.HTTP_200_OK)
async def get_vehicle_by_plate(
    plate: str,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Get vehicle information by plate number.
    """
    try:
        vehicle_repo = VehicleRepositoryImpl()
        plate = plate.upper().strip()
        vehicle = await vehicle_repo.get_by_plate(plate)
        
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with plate {plate} not found"
            )
        
        return {
            "message": "Vehicle retrieved successfully",
            "vehicle": {
                "id": vehicle.id,
                "plate": vehicle.plate,
                "vehicle_type": vehicle.vehicle_type,
                "owner_name": vehicle.owner_name,
                "owner_phone": vehicle.owner_phone,
                "brand": vehicle.brand,
                "model": vehicle.model,
                "color": vehicle.color,
                "is_frequent": vehicle.is_frequent,
                "notes": vehicle.notes
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving vehicle: {str(e)}"
        )


@router.get("/history/{plate}", status_code=status.HTTP_200_OK)
async def get_vehicle_history(
    plate: str,
    limit: int = 10,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Get parking history for a specific vehicle by plate number.
    
    - **plate**: Vehicle license plate
    - **limit**: Maximum number of records to return (default: 10)
    """
    try:
        from app.infrastructure.database.session import SessionLocal
        from app.infrastructure.database.models.vehicles import ParkingRecord as ParkingRecordModel, Vehicle as VehicleModel
        from sqlalchemy import select
        from sqlalchemy.orm import joinedload
        
        plate = plate.upper().strip()
        
        async with SessionLocal() as session:
            # First, get the vehicle
            vehicle_result = await session.execute(
                select(VehicleModel).where(VehicleModel.plate == plate)
            )
            vehicle = vehicle_result.scalar_one_or_none()
            
            if not vehicle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vehicle with plate {plate} not found"
                )
            
            # Get parking records for this vehicle
            result = await session.execute(
                select(ParkingRecordModel)
                .where(ParkingRecordModel.vehicle_id == vehicle.id)
                .order_by(ParkingRecordModel.entry_time.desc())
                .limit(limit)
            )
            records = result.scalars().all()
            
            records_data = []
            for record in records:
                duration_hours = None
                if record.exit_time:
                    duration = record.exit_time - record.entry_time
                    duration_hours = round(duration.total_seconds() / 3600, 2)
                
                records_data.append({
                    "id": record.id,
                    "entry_time": record.entry_time.isoformat(),
                    "exit_time": record.exit_time.isoformat() if record.exit_time else None,
                    "duration_hours": duration_hours,
                    "helmet_count": record.helmet_count,
                    "helmet_charge": record.helmet_charge,
                    "total_cost": record.total_cost,
                    "payment_status": record.payment_status,
                    "notes": record.notes
                })
            
            return {
                "message": "Vehicle history retrieved successfully",
                "vehicle": {
                    "id": vehicle.id,
                    "plate": vehicle.plate,
                    "vehicle_type": vehicle.vehicle_type,
                    "owner_name": vehicle.owner_name,
                    "is_frequent": vehicle.is_frequent
                },
                "total_records": len(records_data),
                "records": records_data
            }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving vehicle history: {str(e)}"
        )


@router.get("/rates", status_code=status.HTTP_200_OK)
async def list_rates(
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    List all active parking rates.
    """
    try:
        rate_repo = RateRepositoryImpl()
        rates = await rate_repo.list_active()
        
        return {
            "message": "Rates retrieved successfully",
            "count": len(rates),
            "rates": [
                {
                    "id": rate.id,
                    "vehicle_type": rate.vehicle_type,
                    "rate_type": rate.rate_type,
                    "price": rate.price,
                    "price_formatted": f"${rate.price / 100:,.0f} COP",
                    "description": rate.description
                }
                for rate in rates
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving rates: {str(e)}"
        )


@router.get("/stats/today", status_code=status.HTTP_200_OK)
async def get_today_stats(
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Get parking statistics for today.
    """
    try:
        from app.infrastructure.database.session import SessionLocal
        from app.infrastructure.database.models.vehicles import ParkingRecord as ParkingRecordModel
        from sqlalchemy import select, func
        from datetime import date
        
        async with SessionLocal() as session:
            today = date.today()
            
            # Total entries today
            total_entries_result = await session.execute(
                select(func.count(ParkingRecordModel.id))
                .where(func.date(ParkingRecordModel.entry_time) == today)
            )
            total_entries = total_entries_result.scalar()
            
            # Active vehicles (currently parked)
            active_result = await session.execute(
                select(func.count(ParkingRecordModel.id))
                .where(ParkingRecordModel.exit_time.is_(None))
            )
            active_count = active_result.scalar()
            
            # Completed today (vehicles that exited today)
            completed_result = await session.execute(
                select(func.count(ParkingRecordModel.id))
                .where(func.date(ParkingRecordModel.exit_time) == today)
            )
            completed_count = completed_result.scalar()
            
            # Total revenue today
            revenue_result = await session.execute(
                select(func.sum(ParkingRecordModel.total_cost))
                .where(func.date(ParkingRecordModel.exit_time) == today)
                .where(ParkingRecordModel.payment_status == "paid")
            )
            total_revenue = revenue_result.scalar() or 0
            
            return {
                "message": "Today's statistics retrieved successfully",
                "date": today.isoformat(),
                "stats": {
                    "total_entries": total_entries,
                    "active_vehicles": active_count,
                    "completed_exits": completed_count,
                    "total_revenue": total_revenue,
                    "total_revenue_formatted": f"${total_revenue / 100:,.0f} COP"
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving statistics: {str(e)}"
        )

