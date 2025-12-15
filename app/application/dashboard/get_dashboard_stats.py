from datetime import date, datetime, timezone
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository
from app.domain.financial.repositories.expense_repository import ExpenseRepository
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository
from app.api.schemas.dashboard_schemas import DashboardStats

class GetDashboardStats:
    def __init__(
        self,
        parking_repo: IParkingRecordRepository,
        washing_repo: IWashingServiceRepository,
        expense_repo: ExpenseRepository,
        subscription_repo: ISubscriptionRepository
    ):
        self.parking_repo = parking_repo
        self.washing_repo = washing_repo
        self.expense_repo = expense_repo
        self.subscription_repo = subscription_repo

    async def execute(self) -> DashboardStats:
        # With TZ=America/Bogota set in Docker, datetime.now() should return local time
        # However, we should be careful. If we use datetime.now(timezone.utc), it's still UTC.
        # If we use datetime.now(), it's local time (naive or aware depending on system).
        # Best practice: Use datetime.now() which will be local time due to TZ env var, 
        # and ensure we query the DB correctly.
        
        today = date.today()
        print(f"DEBUG: Calculating stats for {today} (System Date)")
        
        # 1. Active Vehicles
        active_records = await self.parking_repo.list_active()
        active_vehicles_count = len(active_records)
        print(f"DEBUG: Active vehicles: {active_vehicles_count}")

        # 2. Total Washes Today & Income from Washes
        # Since we set TZ=America/Bogota, the DB queries using 'today' should align 
        # if the DB also respects the timezone or if we query by range.
        washes_today = await self.washing_repo.get_by_date(today)
        total_washes_count = len(washes_today)
        
        washes_income = sum(w.price for w in washes_today if w.payment_status in ['PAID', 'COMPLETED', 'completed', 'paid'])
        print(f"DEBUG: Washes: {total_washes_count}, Income: {washes_income}")

        # 3. Income from Subscriptions Today
        subscriptions_today = await self.subscription_repo.get_by_date_range(today, today)
        subscriptions_income = sum(s.monthly_fee for s in subscriptions_today)
        print(f"DEBUG: Subscriptions Income: {subscriptions_income}")

        # 4. Parking Income Today
        parking_income = await self.parking_repo.get_income_by_date(today)
        print(f"DEBUG: Parking Income: {parking_income}")

        # 5. Expenses Today
        expenses_today = await self.expense_repo.get_by_date_range(today, today)
        total_expenses = sum(e.amount for e in expenses_today)
        print(f"DEBUG: Expenses: {total_expenses}")

        return DashboardStats(
            active_vehicles=active_vehicles_count,
            total_washes=total_washes_count,
            today_income=washes_income + subscriptions_income + parking_income,
            today_expenses=total_expenses
        )
