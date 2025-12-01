from datetime import date
from typing import IO
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.reporting.services.export_service import ExportService
from app.domain.parking.repositories.vehicle_repository import IVehicleRepository

class ExportReportsUseCase:
    """Use case for exporting reports"""
    
    def __init__(
        self,
        parking_record_repo: IParkingRecordRepository,
        vehicle_repo: IVehicleRepository,
        export_service: ExportService
    ):
        self.parking_record_repo = parking_record_repo
        self.vehicle_repo = vehicle_repo
        self.export_service = export_service
    
    async def export_parking_history(
        self, 
        start_date: date, 
        end_date: date, 
        format: str = "csv"
    ) -> IO:
        """
        Export parking history for a date range.
        """
        records = await self.parking_record_repo.list_by_date_range(start_date, end_date)
        
        # Prepare data for export
        data = []
        for record in records:
            vehicle = await self.vehicle_repo.get_by_id(record.vehicle_id)
            plate = vehicle.plate if vehicle else "Unknown"
            
            data.append({
                "ID": record.id,
                "Plate": plate,
                "Entry Time": record.entry_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Exit Time": record.exit_time.strftime("%Y-%m-%d %H:%M:%S") if record.exit_time else "Active",
                "Duration (Hours)": f"{(record.exit_time - record.entry_time).total_seconds() / 3600:.2f}" if record.exit_time else "-",
                "Total Cost": f"${record.total_cost / 100:,.0f}",
                "Status": record.payment_status,
                "Notes": record.notes or ""
            })
            
        if format.lower() == "csv":
            return self.export_service.export_to_csv(data)
        elif format.lower() == "excel":
            return self.export_service.export_to_excel(data)
        elif format.lower() == "pdf":
            return self.export_service.export_to_pdf(data, title=f"Parking History Report ({start_date} to {end_date})")
        else:
            raise ValueError(f"Unsupported format: {format}")
