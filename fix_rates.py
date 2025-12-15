import asyncio
import sys
import os

# Ensure /app is in path
sys.path.append('/app')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import Rate
from sqlalchemy import select

async def fix_rates():
    async with SessionLocal() as session:
        print("Fixing rates...")
        
        # 1. Fix Carro duplicates
        print("Fixing 'Carro' duplicates...")
        result = await session.execute(
            select(Rate)
            .where(Rate.vehicle_type == 'Carro')
            .where(Rate.rate_type == 'Hora')
            .where(Rate.is_active == True)
        )
        car_rates = result.scalars().all()
        
        if len(car_rates) > 1:
            print(f"Found {len(car_rates)} active rates for Carro. Keeping the first one (ID: {car_rates[0].id}) and deactivating others.")
            # Keep the first one, deactivate others
            # Actually, let's keep the one with ID 1 as it looks like the 'original' one, or the one with highest price?
            # Let's keep ID 1 (Price 2000).
            target_id = 1
            for rate in car_rates:
                if rate.id != target_id:
                    print(f"Deactivating Rate ID: {rate.id}")
                    rate.is_active = False
                    session.add(rate)
        elif len(car_rates) == 0:
             print("No active rate for Carro found. Creating one.")
             new_car_rate = Rate(
                 vehicle_type='Carro',
                 rate_type='Hora',
                 price=2000,
                 description='Tarifa por hora para carro',
                 is_active=True
             )
             session.add(new_car_rate)
        else:
            print("Carro rates are fine.")

        # 2. Fix Moto missing
        print("Checking 'Moto' rates...")
        result = await session.execute(
            select(Rate)
            .where(Rate.vehicle_type == 'Moto')
            .where(Rate.rate_type == 'Hora')
            .where(Rate.is_active == True)
        )
        moto_rate = result.scalar_one_or_none()
        
        if not moto_rate:
            print("No active rate found for 'Moto'. Creating one...")
            new_moto_rate = Rate(
                vehicle_type='Moto',
                rate_type='Hora',
                price=1000,
                description='Tarifa por hora para moto',
                is_active=True
            )
            session.add(new_moto_rate)
        else:
            print(f"Moto rate already exists (ID: {moto_rate.id}).")

        await session.commit()
        print("Rates fixed successfully.")

if __name__ == "__main__":
    asyncio.run(fix_rates())
