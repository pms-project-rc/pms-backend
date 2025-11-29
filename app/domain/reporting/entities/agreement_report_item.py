from dataclasses import dataclass

@dataclass
class AgreementReportItem:
    company_name: str
    total_washes: int
    total_amount: int
