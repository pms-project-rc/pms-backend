from fastapi import APIRouter, Depends, Query
from datetime import date
from typing import Optional

from app.application.reporting.services.occupancy_reporting_service import OccupancyReportingService
from app.infrastructure.repositories.reporting.occupancy_reporting_repository_impl import OccupancyReportingRepositoryImpl
from app.application.dto.reporting.occupancy_report_response import OccupancyReportResponse

router = APIRouter()

def get_occupancy_service():
    repo = OccupancyReportingRepositoryImpl()
    return OccupancyReportingService(repo)

@router.get("/occupancy", response_model=OccupancyReportResponse)
async def get_occupancy_report(
    report_date: Optional[date] = Query(None, description="Fecha del reporte (YYYY-MM-DD). Por defecto es hoy."),
    service: OccupancyReportingService = Depends(get_occupancy_service)
):
    """
    Obtiene el reporte de ocupación por hora para una fecha específica.
    """
    if report_date is None:
        report_date = date.today()
        
    return await service.get_occupancy_report(report_date)
