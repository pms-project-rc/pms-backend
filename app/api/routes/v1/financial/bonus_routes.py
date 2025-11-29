from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import date
from typing import List
from app.api.schemas.financial_schemas import BonusCalculationResult, MonthlyBonusResponse
from app.application.financial.services.calculate_daily_bonuses import CalculateDailyBonuses
from app.application.financial.services.get_monthly_bonuses import GetMonthlyBonuses
from app.application.financial.services.apply_advance_deduction import ApplyAdvanceDeduction
from app.infrastructure.repositories.financial.bonus_repository_impl import BonusRepositoryImpl
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.infrastructure.repositories.financial.employee_advance_repository_impl import EmployeeAdvanceRepositoryImpl

router = APIRouter()

@router.post("/calculate-daily", response_model=List[BonusCalculationResult])
async def calculate_daily_bonuses(
    calculation_date: date = Query(default=date.today())
):
    # Repositories
    bonus_repo = BonusRepositoryImpl()
    washing_repo = WashingServiceRepositoryImpl()
    washer_repo = WasherRepositoryImpl()
    advance_repo = EmployeeAdvanceRepositoryImpl()

    # Use Cases
    apply_deduction = ApplyAdvanceDeduction(advance_repo)
    calculate_bonuses = CalculateDailyBonuses(
        bonus_repo,
        washing_repo,
        washer_repo,
        apply_deduction
    )

    try:
        results = await calculate_bonuses.execute(calculation_date)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monthly", response_model=List[MonthlyBonusResponse])
async def get_monthly_bonuses(
    month: int = Query(..., ge=1, le=12),
    year: int = Query(..., ge=2020)
):
    # Repositories
    bonus_repo = BonusRepositoryImpl()
    washer_repo = WasherRepositoryImpl()

    # Use Case
    get_monthly = GetMonthlyBonuses(bonus_repo, washer_repo)

    try:
        return await get_monthly.execute(month, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

