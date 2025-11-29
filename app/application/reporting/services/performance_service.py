from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from app.application.reporting.services.revenue_service import RevenueService
from app.domain.financial.repositories.expense_repository import ExpenseRepository
from app.domain.financial.repositories.bonus_repository import BonusRepository
from app.api.schemas.reporting_schemas import PerformanceReportResponse

class PerformanceService:
    def __init__(
        self, 
        db: AsyncSession, 
        expense_repository: ExpenseRepository,
        bonus_repository: BonusRepository
    ):
        self.db = db
        self.revenue_service = RevenueService(db)
        self.expense_repository = expense_repository
        self.bonus_repository = bonus_repository

    async def calculate_performance(self, start_date: date, end_date: date) -> PerformanceReportResponse:
        # 1. Get Total Revenue
        # We use 'day' grouping but we only care about the total_period_income
        revenue_report = await self.revenue_service.get_consolidated_revenue(start_date, end_date, group_by='day')
        total_income = revenue_report.total_period_income

        # 2. Get Total Expenses
        total_expenses = await self.expense_repository.get_sum_by_date_range(start_date, end_date)

        # 3. Get Total Bonuses
        total_bonuses = await self.bonus_repository.get_sum_by_date_range(start_date, end_date)

        # 4. Calculate Net Performance
        # R = Ingresos – (Gastos + Bonos)
        net_performance = total_income - (total_expenses + total_bonuses)

        return PerformanceReportResponse(
            start_date=start_date,
            end_date=end_date,
            total_income=total_income,
            total_expenses=total_expenses,
            total_bonuses=total_bonuses,
            net_performance=net_performance
        )
