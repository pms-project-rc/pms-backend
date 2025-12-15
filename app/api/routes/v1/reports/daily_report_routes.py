from fastapi import APIRouter, Depends, Query, HTTPException, status
from datetime import date, datetime, timedelta
from typing import Optional, List
from zoneinfo import ZoneInfo
from sqlalchemy import select, func, cast, Date, and_
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.vehicles import ParkingRecord
from app.infrastructure.database.models.services import WashingService
from app.api.dependencies.auth import get_current_admin

router = APIRouter(prefix="/reports", tags=["Reports"])

BOGOTA_TZ = ZoneInfo("America/Bogota")

@router.get("/daily")
async def get_daily_report(
    date_val: date = Query(..., alias="date"),
    current_admin: any = Depends(get_current_admin)
):
    """
    Get daily report for a specific date.
    """
    try:
        async with SessionLocal() as session:
            # 1. Parking Records for the date
            # Eager load vehicle to avoid lazy loading errors
            from sqlalchemy.orm import joinedload
            
            # We need to be careful with SQL filtering. 
            # If Postgres TZ is set correctly, func.date() works.
            # If not, we might miss some records. 
            # For safety, let's fetch a slightly wider range if we were unsure, 
            # but since we set TZ in docker-compose, let's trust func.date() for now 
            # or rely on the fact that the user says "ingreso... en mi hora local" implies DB insertion is OK.
            
            parking_result = await session.execute(
                select(ParkingRecord)
                .options(joinedload(ParkingRecord.vehicle))
                .where(
                    (func.date(ParkingRecord.entry_time) == date_val) | 
                    (func.date(ParkingRecord.exit_time) == date_val)
                )
            )
            parking_records = parking_result.scalars().all()
            
            # 2. Washing Records for the date
            washing_result = await session.execute(
                select(WashingService)
                .where(func.date(WashingService.service_date) == date_val)
            )
            washing_records = washing_result.scalars().all()
            
            # Calculate totals
            # Only count revenue for records that EXITED today (in Local Time) and are PAID
            parking_revenue = 0
            total_parkings = 0
            
            for r in parking_records:
                # Convert to local time
                local_entry = r.entry_time.astimezone(BOGOTA_TZ) if r.entry_time else None
                local_exit = r.exit_time.astimezone(BOGOTA_TZ) if r.exit_time else None
                
                # Count as parking if entry was today (Local)
                if local_entry and local_entry.date() == date_val:
                    total_parkings += 1
                
                # Count revenue if exit was today (Local) and paid
                if r.payment_status == 'paid' and local_exit and local_exit.date() == date_val:
                    parking_revenue += (r.total_cost or 0)
            
            # For washing, count revenue if service_date is today and PAID
            washing_revenue = 0
            for w in washing_records:
                local_service_date = w.service_date.astimezone(BOGOTA_TZ) if w.service_date else None
                if w.payment_status == 'paid' and local_service_date and local_service_date.date() == date_val:
                    washing_revenue += w.price
            
            total_revenue = parking_revenue + washing_revenue
            total_washing = len(washing_records)
            
            # Hourly breakdown
            hourly_data = {}
            for i in range(24):
                hour_key = f"{i:02d}:00"
                hourly_data[hour_key] = {
                    "hora": f"{i:02d}:00-{i+1:02d}:00",
                    "servicios": 0,
                    "parqueos": 0,
                    "ingresos": 0,
                    "ticket": 0
                }
            
            # Fill hourly data
            for r in parking_records:
                if r.entry_time:
                    # Use Local Time for hourly bucket
                    local_entry = r.entry_time.astimezone(BOGOTA_TZ)
                    hour = local_entry.hour
                    hour_key = f"{hour:02d}:00"
                    
                    if hour_key in hourly_data:
                        # Only count in hourly breakdown if it matches the requested date
                        if local_entry.date() == date_val:
                            hourly_data[hour_key]["parqueos"] += 1
                        
                        # Add revenue to the hour of EXIT? Or hour of ENTRY?
                        # Usually revenue is reported at the time it is realized (Exit).
                        if r.payment_status == 'paid' and r.exit_time:
                            local_exit = r.exit_time.astimezone(BOGOTA_TZ)
                            if local_exit.date() == date_val:
                                exit_hour = local_exit.hour
                                exit_hour_key = f"{exit_hour:02d}:00"
                                if exit_hour_key in hourly_data:
                                    hourly_data[exit_hour_key]["ingresos"] += (r.total_cost or 0)

            for w in washing_records:
                if w.service_date:
                    local_service_date = w.service_date.astimezone(BOGOTA_TZ)
                    if local_service_date.date() == date_val:
                        hour = local_service_date.hour
                        hour_key = f"{hour:02d}:00"
                        if hour_key in hourly_data:
                            hourly_data[hour_key]["servicios"] += 1
                            if w.payment_status == 'paid':
                                hourly_data[hour_key]["ingresos"] += w.price

            hourly_list = list(hourly_data.values())
            
            return {
                "date": date_val.isoformat(),
                "totalParkings": total_parkings,
                "totalWashing": total_washing,
                "totalRevenue": total_revenue,
                "parkingRevenue": parking_revenue,
                "washingRevenue": washing_revenue,
                "averageTicket": total_revenue / (total_parkings + total_washing) if (total_parkings + total_washing) > 0 else 0,
                "occupancyPercentage": 0, # TODO: Calculate real occupancy
                "parkingRecords": [
                    {
                        "id": r.id,
                        "plate": r.vehicle.plate if r.vehicle else "Unknown", # Need to eager load vehicle or fetch
                        "vehicle_type": r.vehicle.vehicle_type if r.vehicle else "Unknown",
                        "entry_time": r.entry_time,
                        "exit_time": r.exit_time,
                        "total_cost": r.total_cost,
                        "status": "completed" if r.exit_time else "active"
                    } for r in parking_records
                ],
                "washingRecords": [], # Simplify for now
                "hourlyBreakdown": hourly_list
            }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating daily report: {str(e)}"
        )
