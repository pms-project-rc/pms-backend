import asyncio
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.getcwd(), 'pms-backend'))

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

        print("\nChecking for duplicate active parking records...")
        # Check for multiple active parking records for the same vehicle
        result = await session.execute(
            select(ParkingRecord.vehicle_id, func.count(ParkingRecord.id))
            .where(ParkingRecord.exit_time.is_(None))
            .group_by(ParkingRecord.vehicle_id)
            .having(func.count(ParkingRecord.id) > 1)
        )
        duplicates = result.all()
        if duplicates:
            print(f"Found duplicate active parking records for vehicles: {duplicates}")
        else:
            print("No duplicate active parking records found.")

        print("\nChecking for duplicate vehicles (same plate)...")
        # Check for multiple vehicles with the same plate
        result = await session.execute(
            select(Vehicle.plate, func.count(Vehicle.id))
            .group_by(Vehicle.plate)
            .having(func.count(Vehicle.id) > 1)
        )
        duplicates = result.all()
        if duplicates:
            print(f"Found duplicate vehicles with same plate: {duplicates}")
        else:
            print("No duplicate vehicles found.")

if __name__ == "__main__":
    asyncio.run(check_duplicates())
