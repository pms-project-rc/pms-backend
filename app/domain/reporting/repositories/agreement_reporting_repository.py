from abc import ABC, abstractmethod
from datetime import date
from typing import List
from app.domain.reporting.entities.agreement_report_item import AgreementReportItem

class IAgreementReportingRepository(ABC):
    @abstractmethod
    async def get_agreement_stats(self, start_date: date, end_date: date) -> List[AgreementReportItem]:
        pass
