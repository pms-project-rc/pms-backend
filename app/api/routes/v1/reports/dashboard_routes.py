from fastapi import APIRouter, Depends, Query
from datetime import date, timedelta
from typing import Optional

from app.infrastructure.database.session import get_session
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.reporting.services.dashboard_service import DashboardService
from app.application.reporting.services.revenue_service import RevenueService
from app.application.reporting.services.washing_analytics_service import WashingAnalyticsService

from app.infrastructure.repositories.financial.expense_repository_impl import ExpenseRepositoryImpl
from app.infrastructure.repositories.financial.bonus_repository_impl import BonusRepositoryImpl
from app.infrastructure.repositories.reporting.occupancy_reporting_repository_impl import OccupancyReportingRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl

from app.application.dto.reporting.dashboard_response import DashboardMetricsResponse

router = APIRouter()

def get_dashboard_service(db: AsyncSession = Depends(get_session)):
    revenue_service = RevenueService(db)
    expense_repo = ExpenseRepositoryImpl()
    bonus_repo = BonusRepositoryImpl()
    
    washing_repo = WashingServiceRepositoryImpl()
    washing_analytics = WashingAnalyticsService(washing_repo)
    
    occupancy_repo = OccupancyReportingRepositoryImpl()
    washer_repo = WasherRepositoryImpl()
    
    return DashboardService(
        revenue_service=revenue_service,
        expense_repository=expense_repo,
        bonus_repository=bonus_repo,
        washing_analytics_service=washing_analytics,
        occupancy_repository=occupancy_repo,
        washer_repository=washer_repo
    )

@router.get("/dashboard", response_model=DashboardMetricsResponse)
async def get_dashboard_metrics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    service: DashboardService = Depends(get_dashboard_service)
):
    """
    Obtiene las métricas consolidadas para el dashboard principal.
    Si no se envían fechas, por defecto toma los últimos 30 días.
    """
    if not end_date:
        end_date = date.today()
    if not start_date:
        start_date = end_date - timedelta(days=30)
        
    return await service.get_dashboard_metrics(start_date, end_date)
