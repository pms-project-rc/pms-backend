from fastapi import APIRouter, Depends, Query, HTTPException
from datetime import date, timedelta
from typing import Literal
from app.application.reporting.services.activity_reporting_service import ActivityReportingService
from app.infrastructure.repositories.reporting.activity_reporting_repository_impl import ActivityReportingRepositoryImpl
from app.application.dto.reporting.activity_report_response import ActivityReportResponse

router = APIRouter(prefix="/reports/activity", tags=["Reports"])

def get_service():
    repo = ActivityReportingRepositoryImpl()
    return ActivityReportingService(repo)

@router.get("/", response_model=ActivityReportResponse)
async def get_activity_report(
    start_date: date = Query(default=date.today() - timedelta(days=30)),
    end_date: date = Query(default=date.today()),
    group_by: Literal["day", "week", "month"] = Query(default="day"),
    service: ActivityReportingService = Depends(get_service)
):
    return await service.get_activity_report(start_date, end_date, group_by)
