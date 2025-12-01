import asyncio
import sys
import os

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import Washer
from app.core.security import get_password_hash

async def seed_washers():
    async with SessionLocal() as session:
        # Check if washer exists
        from sqlalchemy import select
        result = await session.execute(select(Washer).where(Washer.email == "washer1@pms.com"))
        washer = result.scalar_one_or_none()
        
        if not washer:
            print("Creating Washer 1...")
            washer = Washer(
                email="washer1@pms.com",
                password_hash=get_password_hash("washer123"),
                full_name="Pedro Lavador",
                phone="3009876543",
                commission_percentage=40,
                is_active=True
            )
            session.add(washer)
            await session.commit()
            print("Washer 1 created successfully!")
        else:
            print("Washer 1 already exists.")

if __name__ == "__main__":
    asyncio.run(seed_washers())
