from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas.financial_schemas import EmployeeAdvanceCreate, EmployeeAdvanceResponse
from app.application.financial.services.register_employee_advance import RegisterEmployeeAdvance
from app.infrastructure.repositories.financial.employee_advance_repository_impl import EmployeeAdvanceRepositoryImpl
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/advances", tags=["Financial"])

def get_repository():
    return EmployeeAdvanceRepositoryImpl()

@router.post("/", response_model=EmployeeAdvanceResponse, status_code=status.HTTP_201_CREATED)
async def create_advance(
    advance: EmployeeAdvanceCreate,
    repository: EmployeeAdvanceRepositoryImpl = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    use_case = RegisterEmployeeAdvance(repository)
    try:
        return await use_case.execute(
            washer_id=advance.washer_id,
            amount=advance.amount,
            installments=advance.installments,
            description=advance.description
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/washer/{washer_id}", response_model=List[EmployeeAdvanceResponse])
async def get_advances_by_washer(
    washer_id: int,
    repository: EmployeeAdvanceRepositoryImpl = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    return await repository.get_active_by_washer(washer_id)
