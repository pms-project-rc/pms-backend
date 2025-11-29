from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from datetime import date, timedelta
from app.application.reporting.services.agreement_reporting_service import AgreementReportingService
from app.infrastructure.repositories.reporting.agreement_reporting_repository_impl import AgreementReportingRepositoryImpl
from app.application.dto.reporting.agreement_report_response import AgreementReportResponse

router = APIRouter(prefix="/reports/agreements", tags=["Reports"])

def get_service():
    repo = AgreementReportingRepositoryImpl()
    return AgreementReportingService(repo)

@router.get("/", response_model=AgreementReportResponse)
async def get_agreement_report(
    start_date: date = Query(default=date.today() - timedelta(days=30)),
    end_date: date = Query(default=date.today()),
    service: AgreementReportingService = Depends(get_service)
):
    return await service.get_report(start_date, end_date)

@router.get("/export/csv")
async def export_agreement_report_csv(
    start_date: date = Query(default=date.today() - timedelta(days=30)),
    end_date: date = Query(default=date.today()),
    service: AgreementReportingService = Depends(get_service)
):
    csv_content = await service.generate_csv(start_date, end_date)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=agreement_report_{start_date}_{end_date}.csv"}
    )
