from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas.shift_schemas import ShiftCreate, ShiftResponse
from app.application.financial.services.start_shift import StartShift
from app.application.financial.services.close_shift import CloseShift
from app.infrastructure.repositories.financial.shift_repository_impl import ShiftRepositoryImpl
from app.infrastructure.repositories.financial.expense_repository_impl import ExpenseRepositoryImpl
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.api.dependencies.auth import get_current_user

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
    current_user = Depends(get_current_user)
):
    use_case = StartShift(shift_repository)
    try:
        return await use_case.execute(admin_id=current_user.id, initial_cash=shift_data.initial_cash)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/close", response_model=ShiftResponse)
async def close_shift(
    shift_repository: ShiftRepositoryImpl = Depends(get_shift_repository),
    expense_repository: ExpenseRepositoryImpl = Depends(get_expense_repository),
    washing_repository: WashingServiceRepositoryImpl = Depends(get_washing_repository),
    parking_repository: ParkingRecordRepositoryImpl = Depends(get_parking_repository),
    current_user = Depends(get_current_user)
):
    use_case = CloseShift(
        shift_repository,
        expense_repository,
        washing_repository,
        parking_repository
    )
    try:
        return await use_case.execute(admin_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
