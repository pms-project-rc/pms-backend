from datetime import date, datetime, time, timedelta
from typing import List, Dict
from collections import defaultdict

from app.application.dto.reporting.dashboard_response import (
    DashboardMetricsResponse, GeneralMetrics, OperationalMetrics, TrendPoint
)
from app.application.reporting.services.revenue_service import RevenueService
from app.domain.financial.repositories.expense_repository import ExpenseRepository
from app.domain.financial.repositories.bonus_repository import BonusRepository
from app.application.reporting.services.washing_analytics_service import WashingAnalyticsService
from app.domain.reporting.repositories.occupancy_reporting_repository import OccupancyReportingRepository
from app.domain.washers.repositories.washer_repository import IWasherRepository

class DashboardService:
    def __init__(
        self,
        revenue_service: RevenueService,
        expense_repository: ExpenseRepository,
        bonus_repository: BonusRepository,
        washing_analytics_service: WashingAnalyticsService,
        occupancy_repository: OccupancyReportingRepository,
        washer_repository: IWasherRepository
    ):
        self.revenue_service = revenue_service
        self.expense_repository = expense_repository
        self.bonus_repository = bonus_repository
        self.washing_analytics_service = washing_analytics_service
        self.occupancy_repository = occupancy_repository
        self.washer_repository = washer_repository

    async def get_dashboard_metrics(self, start_date: date, end_date: date) -> DashboardMetricsResponse:
        # 1. General Metrics
        # Income
        revenue_report = await self.revenue_service.get_consolidated_revenue(start_date, end_date, group_by='day')
        total_income = revenue_report.total_period_income
        
        # Expenses
        total_expenses = await self.expense_repository.get_sum_by_date_range(start_date, end_date)
        daily_expenses = await self.expense_repository.get_daily_expenses(start_date, end_date)
        
        # Bonuses
        total_bonuses = await self.bonus_repository.get_sum_by_date_range(start_date, end_date)
        daily_bonuses = await self.bonus_repository.get_daily_bonuses(start_date, end_date)
        
        # Net Performance
        net_performance = total_income - (total_expenses + total_bonuses)
        
        # Averages
        days_count = (end_date - start_date).days + 1
        avg_daily_income = int(total_income / days_count) if days_count > 0 else 0
        avg_daily_expenses = int(total_expenses / days_count) if days_count > 0 else 0
        
        ratio = 0.0
        if total_expenses > 0:
            ratio = total_income / total_expenses
        elif total_income > 0:
            ratio = float('inf') # Or just total_income if expenses 0? Let's keep it simple.
            
        general_metrics = GeneralMetrics(
            total_income=total_income,
            total_expenses=total_expenses,
            total_bonuses=total_bonuses,
            net_performance=net_performance,
            avg_daily_income=avg_daily_income,
            avg_daily_expenses=avg_daily_expenses,
            income_vs_expenses_ratio=round(ratio, 2)
        )
        
        # 2. Operational Metrics
        # Occupancy
        # Calculate average occupancy: (Total Parking Duration in Hours) / (Total Hours in Period)
        # This gives "Average number of cars parked at any given time"
        start_dt = datetime.combine(start_date, time.min)
        end_dt = datetime.combine(end_date, time.max)
        total_seconds = await self.occupancy_repository.get_total_parking_duration_seconds(start_dt, end_dt)
        
        total_period_hours = (end_dt - start_dt).total_seconds() / 3600.0
        avg_occupancy = 0.0
        if total_period_hours > 0:
            avg_occupancy = (total_seconds / 3600.0) / total_period_hours
            
        # Washing Time
        washing_stats = await self.washing_analytics_service.get_duration_analytics(start_date, end_date)
        total_minutes = 0.0
        total_services = 0
        unique_washers_with_service = set()
        
        for stat in washing_stats.stats:
            total_minutes += stat.avg_duration_minutes * stat.count
            total_services += stat.count
            unique_washers_with_service.add(stat.washer_id)
            
        avg_washing_time = 0.0
        if total_services > 0:
            avg_washing_time = total_minutes / total_services
            
        # Personnel Utilization
        total_active_washers = await self.washer_repository.count_active()
        utilization = 0.0
        if total_active_washers > 0:
            utilization = (len(unique_washers_with_service) / total_active_washers) * 100.0
            
        operational_metrics = OperationalMetrics(
            avg_occupancy_level=round(avg_occupancy, 2),
            avg_washing_time_minutes=round(avg_washing_time, 2),
            personnel_utilization_percentage=round(utilization, 2)
        )
        
        # 3. Trends
        # Merge daily data
        trend_map: Dict[date, TrendPoint] = {}
        
        # Initialize with all dates in range
        current = start_date
        while current <= end_date:
            trend_map[current] = TrendPoint(date=current, income=0, expenses=0, bonuses=0)
            current += timedelta(days=1)
            
        # Fill Income
        for item in revenue_report.data:
            if item.date in trend_map:
                trend_map[item.date].income = item.total_income
                
        # Fill Expenses
        for item in daily_expenses:
            d = item['date']
            if d in trend_map:
                trend_map[d].expenses = item['total']
                
        # Fill Bonuses
        for item in daily_bonuses:
            d = item['date']
            if d in trend_map:
                trend_map[d].bonuses = item['total']
                
        trends = sorted(trend_map.values(), key=lambda x: x.date)
        
        return DashboardMetricsResponse(
            start_date=start_date,
            end_date=end_date,
            general=general_metrics,
            operational=operational_metrics,
            trends=trends
        )
