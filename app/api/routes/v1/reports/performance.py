from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.infrastructure.database.session import get_session
from app.application.reporting.services.performance_service import PerformanceService
from app.infrastructure.repositories.financial.expense_repository_impl import ExpenseRepositoryImpl
from app.infrastructure.repositories.financial.bonus_repository_impl import BonusRepositoryImpl
from app.api.schemas.reporting_schemas import PerformanceReportResponse

router = APIRouter()

@router.get("/performance", response_model=PerformanceReportResponse)
async def get_performance_report(
    start_date: date = Query(..., description="Fecha de inicio del reporte"),
    end_date: date = Query(..., description="Fecha de fin del reporte"),
    db: AsyncSession = Depends(get_session)
):
    """
    Obtiene el reporte de rendimiento operativo (Ingresos - Gastos - Bonos).
    """
    expense_repo = ExpenseRepositoryImpl()
    bonus_repo = BonusRepositoryImpl()
    service = PerformanceService(db, expense_repo, bonus_repo)
    
    return await service.calculate_performance(start_date, end_date)
