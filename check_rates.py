import asyncio
import sys
import os

# Ensure /app is in path
sys.path.append('/app')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import Rate
from sqlalchemy import select

async def check_rates():
    async with SessionLocal() as session:
        print("Checking Rates table...")
        result = await session.execute(select(Rate))
        rates = result.scalars().all()
        
        if not rates:
            print("No rates found in the database.")
        else:
            print(f"Found {len(rates)} rates:")
            for rate in rates:
                print(f"ID: {rate.id}, Type: '{rate.vehicle_type}', Rate Type: '{rate.rate_type}', Price: {rate.price}, Active: {rate.is_active}")

if __name__ == "__main__":
    asyncio.run(check_rates())
