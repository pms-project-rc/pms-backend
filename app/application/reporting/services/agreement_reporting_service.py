from datetime import date
import csv
import io
from app.domain.reporting.repositories.agreement_reporting_repository import IAgreementReportingRepository
from app.application.dto.reporting.agreement_report_response import AgreementReportResponse, AgreementReportItem as DTOAgreementReportItem

class AgreementReportingService:
    def __init__(self, repo: IAgreementReportingRepository):
        self.repo = repo

    async def get_report(self, start_date: date, end_date: date) -> AgreementReportResponse:
        domain_items = await self.repo.get_agreement_stats(start_date, end_date)
        
        dto_items = [
            DTOAgreementReportItem(
                company_name=item.company_name,
                total_washes=item.total_washes,
                total_amount=item.total_amount
            ) for item in domain_items
        ]
        
        return AgreementReportResponse(
            start_date=start_date,
            end_date=end_date,
            items=dto_items
        )

    async def generate_csv(self, start_date: date, end_date: date) -> str:
        report = await self.get_report(start_date, end_date)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(["Company Name", "Total Washes", "Total Amount (COP)"])
        
        # Rows
        for item in report.items:
            writer.writerow([
                item.company_name, 
                item.total_washes, 
                item.total_amount / 100.0 # Convert cents to units
            ])
            
        return output.getvalue()
