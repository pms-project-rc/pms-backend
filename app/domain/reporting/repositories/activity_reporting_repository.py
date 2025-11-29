from abc import ABC, abstractmethod
from datetime import date
from typing import List
from app.domain.reporting.entities.activity_report_item import ActivityReportItem

class IActivityReportingRepository(ABC):
    @abstractmethod
    async def get_daily_activity(self, start_date: date, end_date: date) -> List[ActivityReportItem]:
        pass
