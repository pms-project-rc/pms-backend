import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import Rate
from sqlalchemy import select

async def check_rates():
    async with SessionLocal() as session:
        result = await session.execute(select(Rate))
        rates = result.scalars().all()
        print(f"Total rates: {len(rates)}")
        for r in rates:
            print(f"ID: {r.id}, Vehicle: '{r.vehicle_type}', Type: '{r.rate_type}', Active: {r.is_active}")

if __name__ == "__main__":
    asyncio.run(check_rates())
