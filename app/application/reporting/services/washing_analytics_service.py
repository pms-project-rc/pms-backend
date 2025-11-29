from datetime import date, timedelta
from typing import List
from app.domain.washing.repositories.washing_service_repository import WashingServiceRepository
from app.api.schemas.reporting_schemas import WashingAnalyticsResponse, WashingDurationStat

class WashingAnalyticsService:
    def __init__(self, washing_repository: WashingServiceRepository):
        self.washing_repository = washing_repository

    async def get_duration_analytics(self, start_date: date, end_date: date) -> WashingAnalyticsResponse:
        raw_stats = await self.washing_repository.get_washing_duration_stats(start_date, end_date)
        
        stats = []
        for row in raw_stats:
            avg_duration = row['avg_duration']
            # avg_duration is a timedelta, convert to minutes
            minutes = 0.0
            if avg_duration:
                minutes = avg_duration.total_seconds() / 60.0
            
            stats.append(WashingDurationStat(
                washer_id=row['washer_id'],
                service_type=row['service_type'],
                avg_duration_minutes=round(minutes, 2),
                count=row['count']
            ))
            
        return WashingAnalyticsResponse(
            start_date=start_date,
            end_date=end_date,
            stats=stats
        )
