from fastapi import APIRouter, Depends, Query
from datetime import date
from app.application.reporting.services.washing_analytics_service import WashingAnalyticsService
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl
from app.api.schemas.reporting_schemas import WashingAnalyticsResponse

router = APIRouter()

@router.get("/washing-analytics", response_model=WashingAnalyticsResponse)
async def get_washing_analytics(
    start_date: date = Query(..., description="Fecha de inicio"),
    end_date: date = Query(..., description="Fecha de fin")
):
    """
    Obtiene estadísticas de tiempos de lavado.
    """
    repo = WashingServiceRepositoryImpl()
    service = WashingAnalyticsService(repo)
    return await service.get_duration_analytics(start_date, end_date)
