from fastapi import APIRouter, Depends, HTTPException, status
from datetime import date, datetime, timezone
from sqlalchemy import select, func
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.vehicles import ParkingRecord
from app.infrastructure.database.models.services import WashingService
from app.infrastructure.database.models.subscriptions import MonthlySubscription
from app.infrastructure.database.models.financial import Shift
from app.api.dependencies.auth import get_current_operational_admin
from app.infrastructure.database.models.users import OperationalAdmin

router = APIRouter(prefix="/stats", tags=["Statistics & Reports"])

@router.get("/summary")
async def get_summary_stats(
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Get comprehensive summary statistics for today.
    Includes parking, washing, subscriptions, and shift data.
    """
    try:
        async with SessionLocal() as session:
            today = date.today()
            
            # Parking stats
            parking_entries = await session.execute(
                select(func.count(ParkingRecord.id))
                .where(func.date(ParkingRecord.entry_time) == today)
            )
            total_entries = parking_entries.scalar() or 0
            
            parking_active = await session.execute(
                select(func.count(ParkingRecord.id))
                .where(ParkingRecord.exit_time.is_(None))
            )
            active_vehicles = parking_active.scalar() or 0
            
            parking_revenue = await session.execute(
                select(func.sum(ParkingRecord.total_cost))
                .where(func.date(ParkingRecord.exit_time) == today)
                .where(ParkingRecord.payment_status == 'paid')
            )
            parking_income = parking_revenue.scalar() or 0
            
            # Washing stats
            washing_active = await session.execute(
                select(func.count(WashingService.id))
                .where(WashingService.end_time.is_(None))
            )
            active_washes = washing_active.scalar() or 0
            
            washing_today = await session.execute(
                select(func.count(WashingService.id))
                .where(func.date(WashingService.service_date) == today)
            )
            total_washes_today = washing_today.scalar() or 0
            
            washing_revenue = await session.execute(
                select(func.sum(WashingService.price))
                .where(func.date(WashingService.service_date) == today)
                .where(WashingService.payment_status == 'paid')
            )
            washing_income = washing_revenue.scalar() or 0
            
            # Subscription stats
            subscriptions_active = await session.execute(
                select(func.count(MonthlySubscription.id))
                .where(MonthlySubscription.start_date <= today)
                .where(MonthlySubscription.end_date >= today)
                .where(MonthlySubscription.payment_status == 'paid')
            )
            total_subscriptions = subscriptions_active.scalar() or 0
            
            # Shift stats
            active_shifts = await session.execute(
                select(func.count(Shift.id))
                .where(Shift.shift_date == today)
                .where(Shift.end_time.is_(None))
            )
            open_shifts = active_shifts.scalar() or 0
            
            # Calculate totals
            total_income = parking_income + washing_income
            
            return {
                "date": today.isoformat(),
                "parking": {
                    "total_entries": total_entries,
                    "active_vehicles": active_vehicles,
                    "income": parking_income,
                    "income_formatted": f"${parking_income / 100:,.0f} COP"
                },
                "washing": {
                    "total_services": total_washes_today,
                    "active_services": active_washes,
                    "income": washing_income,
                    "income_formatted": f"${washing_income / 100:,.0f} COP"
                },
                "subscriptions": {
                    "active_count": total_subscriptions
                },
                "shifts": {
                    "open_count": open_shifts
                },
                "totals": {
                    "total_income": total_income,
                    "total_income_formatted": f"${total_income / 100:,.0f} COP"
                }
            }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving summary stats: {str(e)}"
        )
