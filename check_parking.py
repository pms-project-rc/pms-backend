import asyncio
import sys
import os
from datetime import date, datetime

# Ensure /app is in path
sys.path.append('/app')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.vehicles import ParkingRecord
from sqlalchemy import select, func

async def check_parking_records():
    async with SessionLocal() as session:
        print(f"Checking Parking Records for today: {date.today()}")
        
        # Get all records for today (entry or exit)
        result = await session.execute(
            select(ParkingRecord)
            .where(
                (func.date(ParkingRecord.entry_time) == date.today()) | 
                (func.date(ParkingRecord.exit_time) == date.today())
            )
        )
        records = result.scalars().all()
        
        print(f"Found {len(records)} records relevant to today:")
        total_income = 0
        for r in records:
            entry_str = r.entry_time.strftime('%Y-%m-%d %H:%M:%S')
            exit_str = r.exit_time.strftime('%Y-%m-%d %H:%M:%S') if r.exit_time else "Active"
            print(f"ID: {r.id}, Plate: {r.vehicle_id}, Entry: {entry_str}, Exit: {exit_str}, Cost: {r.total_cost}, Status: {r.payment_status}")
            if r.payment_status == 'paid':
                total_income += (r.total_cost or 0)
        
        print(f"Calculated Total Income (Paid): {total_income}")

if __name__ == "__main__":
    asyncio.run(check_parking_records())
