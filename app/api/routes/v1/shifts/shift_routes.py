from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas.shift_schemas import ShiftCreate, ShiftResponse
from app.application.financial.services.start_shift import StartShift
from app.application.financial.services.close_shift import CloseShift
from app.infrastructure.repositories.financial.shift_repository_impl import ShiftRepositoryImpl
from app.infrastructure.repositories.financial.expense_repository_impl import ExpenseRepositoryImpl
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.api.dependencies.auth import get_current_admin, get_current_user_any

router = APIRouter(prefix="/shifts", tags=["Shifts"])

def get_shift_repository():
    return ShiftRepositoryImpl()

def get_expense_repository():
    return ExpenseRepositoryImpl()

def get_washing_repository():
    return WashingServiceRepositoryImpl()

def get_parking_repository():
    return ParkingRecordRepositoryImpl()

@router.post("/start", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def start_shift(
    shift_data: ShiftCreate,
    shift_repository: ShiftRepositoryImpl = Depends(get_shift_repository),
    current_user = Depends(get_current_user_any)
):
    use_case = StartShift(shift_repository)
    try:
        # Si es un lavador, pasar washer_id; si es admin, pasar admin_id
        if current_user.__class__.__name__ == 'Washer':
            return await use_case.execute(washer_id=current_user.id, initial_cash=shift_data.initial_cash)
        else:
            return await use_case.execute(admin_id=current_user.id, initial_cash=shift_data.initial_cash)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/close", response_model=ShiftResponse)
async def close_shift(
    shift_repository: ShiftRepositoryImpl = Depends(get_shift_repository),
    expense_repository: ExpenseRepositoryImpl = Depends(get_expense_repository),
    washing_repository: WashingServiceRepositoryImpl = Depends(get_washing_repository),
    parking_repository: ParkingRecordRepositoryImpl = Depends(get_parking_repository),
    current_user = Depends(get_current_user_any)
):
    use_case = CloseShift(
        shift_repository,
        expense_repository,
        washing_repository,
        parking_repository
    )
    try:
        # Si es un lavador, pasar washer_id; si es admin, pasar admin_id
        if current_user.__class__.__name__ == 'Washer':
            return await use_case.execute(admin_id=None, washer_id=current_user.id)
        else:
            return await use_case.execute(admin_id=current_user.id, washer_id=None)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/active", response_model=ShiftResponse, status_code=status.HTTP_200_OK)
async def get_active_shift(
    shift_repository: ShiftRepositoryImpl = Depends(get_shift_repository),
    current_user = Depends(get_current_user_any)
):
    """Get the current active shift for the logged-in user (admin or washer)"""
    active_shift = await shift_repository.get_active_shift_by_admin(current_user.id)
    if not active_shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active shift found"
        )
    return active_shift
