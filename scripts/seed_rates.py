import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import Rate
from sqlalchemy import select

async def seed_rates():
    async with SessionLocal() as session:
        # Check if rates already exist
        result = await session.execute(select(Rate))
        existing_rates = result.scalars().all()
        
        if existing_rates:
            print(f"Rates already exist ({len(existing_rates)} rates found). Skipping seed.")
            return
        
        # Define default rates (prices in centavos - Colombian pesos)
        rates = [
            # Motorcycle rates
            Rate(
                vehicle_type="Moto",
                rate_type="Hora",
                price=200000,  # 2,000 pesos per hour
                description="Tarifa por hora para motos",
                is_active=True
            ),
            Rate(
                vehicle_type="Moto",
                rate_type="Día",
                price=1000000,  # 10,000 pesos per day
                description="Tarifa por día para motos",
                is_active=True
            ),
            Rate(
                vehicle_type="Moto",
                rate_type="Noche",
                price=500000,  # 5,000 pesos per night
                description="Tarifa por noche para motos",
                is_active=True
            ),
            
            # Car rates
            Rate(
                vehicle_type="Carro",
                rate_type="Hora",
                price=300000,  # 3,000 pesos per hour
                description="Tarifa por hora para carros",
                is_active=True
            ),
            Rate(
                vehicle_type="Carro",
                rate_type="Día",
                price=1500000,  # 15,000 pesos per day
                description="Tarifa por día para carros",
                is_active=True
            ),
            Rate(
                vehicle_type="Carro",
                rate_type="Noche",
                price=800000,  # 8,000 pesos per night
                description="Tarifa por noche para carros",
                is_active=True
            ),
            
            # Bicycle rates
            Rate(
                vehicle_type="Bicicleta",
                rate_type="Hora",
                price=100000,  # 1,000 pesos per hour
                description="Tarifa por hora para bicicletas",
                is_active=True
            ),
            Rate(
                vehicle_type="Bicicleta",
                rate_type="Día",
                price=500000,  # 5,000 pesos per day
                description="Tarifa por día para bicicletas",
                is_active=True
            ),
        ]
        
        # Add all rates to session
        for rate in rates:
            session.add(rate)
        
        await session.commit()
        print(f"✓ {len(rates)} rates created successfully!")
        
        # Display created rates
        print("\nCreated rates:")
        for rate in rates:
            print(f"  - {rate.vehicle_type} ({rate.rate_type}): ${rate.price / 100:.0f} COP")

if __name__ == "__main__":
    asyncio.run(seed_rates())
