from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, cast, Date
from datetime import date, timedelta
from typing import List, Dict
from collections import defaultdict
from app.infrastructure.database.models.vehicles import ParkingRecord
from app.infrastructure.database.models.services import WashingService
from app.infrastructure.database.models.subscriptions import MonthlySubscription
from app.api.schemas.reporting_schemas import RevenueStats, RevenueReportResponse

class RevenueService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_consolidated_revenue(self, start_date: date, end_date: date, group_by: str = 'day') -> RevenueReportResponse:
        # Initialize a dictionary to hold stats for each date
        daily_stats: Dict[date, RevenueStats] = defaultdict(lambda: RevenueStats(date=date.today()))

        def get_stat(d: date) -> RevenueStats:
            if d not in daily_stats:
                daily_stats[d] = RevenueStats(date=d)
            return daily_stats[d]

        # 1. Parking Revenue
        stmt_parking = (
            select(
                cast(ParkingRecord.entry_time, Date).label('date'),
                func.sum(ParkingRecord.total_cost).label('total')
            )
            .where(ParkingRecord.payment_status == 'paid')
            .where(cast(ParkingRecord.entry_time, Date) >= start_date)
            .where(cast(ParkingRecord.entry_time, Date) <= end_date)
            .group_by(cast(ParkingRecord.entry_time, Date))
        )
        result_parking = await self.db.execute(stmt_parking)
        for row in result_parking:
            stat = get_stat(row.date)
            stat.parking_income = row.total or 0
            stat.total_income += stat.parking_income

        # 2. Washing Revenue
        stmt_washing = (
            select(
                cast(WashingService.service_date, Date).label('date'),
                func.sum(WashingService.price).label('total')
            )
            .where(WashingService.payment_status == 'paid')
            .where(cast(WashingService.service_date, Date) >= start_date)
            .where(cast(WashingService.service_date, Date) <= end_date)
            .group_by(cast(WashingService.service_date, Date))
        )
        result_washing = await self.db.execute(stmt_washing)
        for row in result_washing:
            stat = get_stat(row.date)
            stat.washing_income = row.total or 0
            stat.total_income += stat.washing_income

        # 3. Subscription Revenue
        stmt_sub = (
            select(
                MonthlySubscription.start_date.label('date'),
                func.sum(MonthlySubscription.monthly_fee).label('total')
            )
            .where(MonthlySubscription.payment_status == 'paid')
            .where(MonthlySubscription.start_date >= start_date)
            .where(MonthlySubscription.start_date <= end_date)
            .group_by(MonthlySubscription.start_date)
        )
        result_sub = await self.db.execute(stmt_sub)
        for row in result_sub:
            stat = get_stat(row.date)
            stat.subscription_income = row.total or 0
            stat.total_income += stat.subscription_income

        # Convert to list and sort
        sorted_stats = sorted(daily_stats.values(), key=lambda x: x.date)

        # Handle Grouping
        final_data = []
        if group_by == 'day':
            final_data = sorted_stats
        elif group_by == 'week':
            final_data = self._group_by_week(sorted_stats)
        elif group_by == 'month':
            final_data = self._group_by_month(sorted_stats)
        
        total_period_income = sum(item.total_income for item in final_data)

        return RevenueReportResponse(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
            data=final_data,
            total_period_income=total_period_income
        )

    def _group_by_week(self, stats: List[RevenueStats]) -> List[RevenueStats]:
        weekly_map: Dict[date, RevenueStats] = {}
        
        for stat in stats:
            # Find the start of the week (Monday)
            start_of_week = stat.date - timedelta(days=stat.date.weekday())
            
            if start_of_week not in weekly_map:
                weekly_map[start_of_week] = RevenueStats(date=start_of_week)
            
            agg = weekly_map[start_of_week]
            agg.parking_income += stat.parking_income
            agg.washing_income += stat.washing_income
            agg.subscription_income += stat.subscription_income
            agg.total_income += stat.total_income
            
        return sorted(weekly_map.values(), key=lambda x: x.date)

    def _group_by_month(self, stats: List[RevenueStats]) -> List[RevenueStats]:
        monthly_map: Dict[date, RevenueStats] = {}
        
        for stat in stats:
            # Find the start of the month
            start_of_month = stat.date.replace(day=1)
            
            if start_of_month not in monthly_map:
                monthly_map[start_of_month] = RevenueStats(date=start_of_month)
            
            agg = monthly_map[start_of_month]
            agg.parking_income += stat.parking_income
            agg.washing_income += stat.washing_income
            agg.subscription_income += stat.subscription_income
            agg.total_income += stat.total_income
            
        return sorted(monthly_map.values(), key=lambda x: x.date)
