from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from datetime import date, timedelta
from typing import Optional

from app.application.reports.export_reports_use_case import ExportReportsUseCase
from app.domain.reporting.services.export_service import ExportService
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.infrastructure.repositories.parking.vehicle_repository_impl import VehicleRepositoryImpl
from app.api.dependencies.auth import get_current_admin

router = APIRouter(prefix="/export", tags=["Reports Export"])

@router.get("/parking-history")
async def export_parking_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", enum=["csv", "excel", "pdf"]),
    current_admin: any = Depends(get_current_admin)
):
    """
    Export parking history report.
    If dates are not provided, defaults to last 30 days.
    """
    try:
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        parking_repo = ParkingRecordRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        export_service = ExportService()
        
        use_case = ExportReportsUseCase(parking_repo, vehicle_repo, export_service)
        
        file_stream = await use_case.export_parking_history(start_date, end_date, format)
        
        media_type = "text/csv"
        filename = f"parking_history_{start_date}_{end_date}.csv"
        
        if format == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"parking_history_{start_date}_{end_date}.xlsx"
        elif format == "pdf":
            media_type = "application/pdf"
            filename = f"parking_history_{start_date}_{end_date}.pdf"
            
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        
        return StreamingResponse(file_stream, media_type=media_type, headers=headers)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )
