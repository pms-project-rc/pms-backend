import asyncio
import sys
import os

# Ensure /app is in path
sys.path.append('/app')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.financial import Shift
from app.infrastructure.database.models.vehicles import Vehicle, ParkingRecord
from sqlalchemy import select, func

async def check_duplicates():
    async with SessionLocal() as session:
        print("Checking for duplicate active shifts...")
        # Check for multiple active shifts for the same admin
        result = await session.execute(
            select(Shift.admin_id, func.count(Shift.id))
            .where(Shift.end_time.is_(None))
            .group_by(Shift.admin_id)
            .having(func.count(Shift.id) > 1)
        )
        duplicates = result.all()
        if duplicates:
            print(f"Found duplicate active shifts for admins: {duplicates}")
            for admin_id, count in duplicates:
                shifts = await session.execute(
                    select(Shift).where(Shift.admin_id == admin_id).where(Shift.end_time.is_(None))
                )
                for shift in shifts.scalars():
                    print(f"Shift ID: {shift.id}, Admin ID: {shift.admin_id}, Start Time: {shift.start_time}")
        else:
            print("No duplicate active shifts found.")

if __name__ == "__main__":
    asyncio.run(check_duplicates())
