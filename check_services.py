"""
Script para verificar servicios de lavado en la base de datos
"""
import asyncio
from sqlalchemy import select, func
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import WashingService as WashingServiceModel
from app.infrastructure.database.models.users import Washer

async def check_services():
    async with SessionLocal() as session:
        # Contar total de servicios
        result = await session.execute(select(func.count(WashingServiceModel.id)))
        total_services = result.scalar()
        print(f"📊 Total services in database: {total_services}")
        
        # Contar servicios por washer
        result = await session.execute(
            select(WashingServiceModel.washer_id, func.count(WashingServiceModel.id))
            .group_by(WashingServiceModel.washer_id)
        )
        for washer_id, count in result:
            if washer_id:
                washer_result = await session.execute(
                    select(Washer).where(Washer.id == washer_id)
                )
                washer = washer_result.scalar_one_or_none()
                print(f"  👤 Washer ID {washer_id} ({washer.email if washer else 'UNKNOWN'}): {count} services")
            else:
                print(f"  ❓ Unassigned: {count} services")
        
        # Mostrar servicios del primer lavador
        result = await session.execute(
            select(WashingServiceModel)
            .where(WashingServiceModel.washer_id == 1)
            .limit(5)
        )
        services = result.scalars().all()
        print(f"\n📋 Services for washer ID 1:")
        if not services:
            print("  ❌ No services found")
        else:
            for s in services:
                print(f"  - ID: {s.id}, Type: {s.service_type}, Price: {s.price}, Status: start_time={s.start_time is not None}, end_time={s.end_time is not None}")

if __name__ == "__main__":
    asyncio.run(check_services())
