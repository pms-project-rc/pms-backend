import asyncio
import sys
import os

# Add parent dir to path to allow imports
sys.path.append(os.getcwd())

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import WashingService
from sqlalchemy import select

async def list_washes():
    async with SessionLocal() as session:
        result = await session.execute(select(WashingService))
        washes = result.scalars().all()
        print(f"Total washes found: {len(washes)}")
        for w in washes:
            print(f"ID: {w.id}, Plate: {w.vehicle_id}, Status: {w.payment_status}, EndTime: {w.end_time}, Date: {w.service_date}")

if __name__ == "__main__":
    asyncio.run(list_washes())
