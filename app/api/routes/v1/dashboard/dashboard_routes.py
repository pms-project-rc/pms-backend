from fastapi import APIRouter, Depends, status
from app.api.schemas.dashboard_schemas import DashboardStats
from app.application.dashboard.get_dashboard_stats import GetDashboardStats
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.infrastructure.repositories.washing.washing_service_repository_impl import WashingServiceRepositoryImpl
from app.infrastructure.repositories.financial.expense_repository_impl import ExpenseRepositoryImpl
from app.infrastructure.repositories.subscriptions.subscription_repository_impl import SubscriptionRepositoryImpl
from app.api.dependencies.auth import get_current_admin

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

def get_dashboard_stats_use_case() -> GetDashboardStats:
    parking_repo = ParkingRecordRepositoryImpl()
    washing_repo = WashingServiceRepositoryImpl()
    expense_repo = ExpenseRepositoryImpl()
    subscription_repo = SubscriptionRepositoryImpl()
    return GetDashboardStats(parking_repo, washing_repo, expense_repo, subscription_repo)

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    current_admin: any = Depends(get_current_admin),
    use_case: GetDashboardStats = Depends(get_dashboard_stats_use_case)
):
    """
    Get dashboard statistics for today.
    """
    return await use_case.execute()
