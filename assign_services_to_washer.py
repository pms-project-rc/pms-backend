"""
Script para asignar servicios a un lavador específico para pruebas
"""
import asyncio
from sqlalchemy import select
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import Washer
from app.infrastructure.database.models.services import WashingService as WashingServiceModel
from datetime import datetime, timezone

async def assign_services():
    async with SessionLocal() as session:
        # Obtener el primer lavador activo
        result = await session.execute(
            select(Washer).where(Washer.is_active == True).limit(1)
        )
        washer = result.scalar_one_or_none()
        
        if not washer:
            print("❌ No active washers found")
            return
        
        print(f"✅ Found washer: {washer.email} (ID: {washer.id})")
        
        # Obtener servicios sin asignar
        result = await session.execute(
            select(WashingServiceModel)
            .where(WashingServiceModel.washer_id.is_(None))
            .limit(5)
        )
        services = result.scalars().all()
        
        if not services:
            print("⚠️  No unassigned services found")
            return
        
        print(f"📋 Found {len(services)} unassigned services")
        
        # Asignar los servicios al lavador
        for service in services:
            service.washer_id = washer.id
            print(f"✓ Assigned service {service.id} to washer {washer.email}")
        
        await session.commit()
        print(f"\n✅ Successfully assigned {len(services)} services to {washer.email}")

if __name__ == "__main__":
    asyncio.run(assign_services())
