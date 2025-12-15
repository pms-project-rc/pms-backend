from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from datetime import date, timedelta
from typing import Optional

from app.application.reports.export_reports_use_case import ExportReportsUseCase
from app.domain.reporting.services.export_service import ExportService
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.infrastructure.repositories.parking.vehicle_repository_impl import VehicleRepositoryImpl
from app.infrastructure.repositories.financial.expense_repository_impl import ExpenseRepositoryImpl
from app.infrastructure.repositories.subscriptions.subscription_repository_impl import SubscriptionRepositoryImpl
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.api.dependencies.auth import get_current_admin

router = APIRouter(prefix="/export", tags=["Reports Export"])

@router.get("/washing-history")
async def export_washing_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", enum=["csv", "excel", "pdf", "json"]),
    current_admin: any = Depends(get_current_admin)
):
    """
    Export washing service history report.
    If dates are not provided, defaults to last 30 days.
    """
    try:
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        parking_repo = ParkingRecordRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        washing_repo = WashingServiceRepositoryImpl()
        export_service = ExportService()
        
        use_case = ExportReportsUseCase(
            parking_record_repo=parking_repo, 
            vehicle_repo=vehicle_repo, 
            export_service=export_service,
            washing_repo=washing_repo
        )
        
        result = await use_case.export_washing_history(start_date, end_date, format)
        
        if format == "json":
            return result
            
        file_stream = result
        
        media_type = "text/csv"
        filename = f"washing_history_{start_date}_{end_date}.csv"
        
        if format == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"washing_history_{start_date}_{end_date}.xlsx"
        elif format == "pdf":
            media_type = "application/pdf"
            filename = f"washing_history_{start_date}_{end_date}.pdf"
            
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        
        return StreamingResponse(file_stream, media_type=media_type, headers=headers)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )

@router.get("/parking-history")
async def export_parking_history(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", enum=["csv", "excel", "pdf", "json"]),
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
        
        result = await use_case.export_parking_history(start_date, end_date, format)
        
        if format == "json":
            return result
            
        file_stream = result
        
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


@router.get("/revenue")
async def export_revenue(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", enum=["csv", "excel", "pdf", "json"]),
    current_admin: any = Depends(get_current_admin)
):
    """
    Export consolidated revenue report.
    If dates are not provided, defaults to last 30 days.
    """
    try:
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        parking_repo = ParkingRecordRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        expense_repo = ExpenseRepositoryImpl()
        subscription_repo = SubscriptionRepositoryImpl()
        washing_repo = WashingServiceRepositoryImpl()
        washer_repo = WasherRepositoryImpl()
        export_service = ExportService()
        
        use_case = ExportReportsUseCase(
            parking_record_repo=parking_repo, 
            vehicle_repo=vehicle_repo, 
            export_service=export_service, 
            expense_repo=expense_repo, 
            subscription_repo=subscription_repo,
            washing_repo=washing_repo,
            washer_repo=washer_repo
        )
        
        result = await use_case.export_consolidated_revenue(start_date, end_date, format)
        
        if format == "json":
            return result
            
        file_stream = result
        
        media_type = "text/csv"
        filename = f"revenue_report_{start_date}_{end_date}.csv"
        
        if format == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"revenue_report_{start_date}_{end_date}.xlsx"
        elif format == "pdf":
            media_type = "application/pdf"
            filename = f"revenue_report_{start_date}_{end_date}.pdf"
            
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        
        return StreamingResponse(file_stream, media_type=media_type, headers=headers)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )

@router.get("/payroll/summary")
async def export_payroll_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", enum=["csv", "excel", "pdf", "json"]),
    current_admin: any = Depends(get_current_admin)
):
    """
    Export payroll summary report (all washers).
    """
    try:
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        parking_repo = ParkingRecordRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        washer_repo = WasherRepositoryImpl()
        export_service = ExportService()
        
        use_case = ExportReportsUseCase(
            parking_record_repo=parking_repo, 
            vehicle_repo=vehicle_repo, 
            export_service=export_service,
            washer_repo=washer_repo
        )
        
        result = await use_case.export_payroll_summary(start_date, end_date, format)
        
        if format == "json":
            return result
            
        file_stream = result
        
        media_type = "text/csv"
        filename = f"payroll_summary_{start_date}_{end_date}.csv"
        
        if format == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"payroll_summary_{start_date}_{end_date}.xlsx"
        elif format == "pdf":
            media_type = "application/pdf"
            filename = f"payroll_summary_{start_date}_{end_date}.pdf"
            
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        
        return StreamingResponse(file_stream, media_type=media_type, headers=headers)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )

@router.get("/payroll/detail/{washer_id}")
async def export_payroll_detail(
    washer_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    format: str = Query("csv", enum=["csv", "excel", "pdf", "json"]),
    current_admin: any = Depends(get_current_admin)
):
    """
    Export payroll detail report for a specific washer.
    """
    try:
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
            
        parking_repo = ParkingRecordRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        washer_repo = WasherRepositoryImpl()
        export_service = ExportService()
        
        use_case = ExportReportsUseCase(
            parking_record_repo=parking_repo, 
            vehicle_repo=vehicle_repo, 
            export_service=export_service,
            washer_repo=washer_repo
        )
        
        result = await use_case.export_payroll_detail(washer_id, start_date, end_date, format)
        
        if format == "json":
            return result
            
        file_stream = result
        
        media_type = "text/csv"
        filename = f"payroll_detail_{washer_id}_{start_date}_{end_date}.csv"
        
        if format == "excel":
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"payroll_detail_{washer_id}_{start_date}_{end_date}.xlsx"
        elif format == "pdf":
            media_type = "application/pdf"
            filename = f"payroll_detail_{washer_id}_{start_date}_{end_date}.pdf"
            
        headers = {
            "Content-Disposition": f"attachment; filename={filename}"
        }
        
        return StreamingResponse(file_stream, media_type=media_type, headers=headers)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting report: {str(e)}"
        )
