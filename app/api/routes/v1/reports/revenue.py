from fastapi import APIRouter, Depends, Query
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.infrastructure.database.session import get_session
from app.application.reporting.services.revenue_service import RevenueService
from app.api.schemas.reporting_schemas import RevenueReportResponse

router = APIRouter(prefix="/revenue", tags=["Reports"])

@router.get("/", response_model=RevenueReportResponse)
async def get_revenue_report(
    start_date: date = Query(..., description="Start date for the report"),
    end_date: date = Query(..., description="End date for the report"),
    group_by: str = Query("day", enum=["day", "week", "month"], description="Group results by day, week, or month"),
    db: AsyncSession = Depends(get_session)
):
    service = RevenueService(db)
    return await service.get_consolidated_revenue(start_date, end_date, group_by)
