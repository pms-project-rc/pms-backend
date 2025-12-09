"""
Script para crear servicios de prueba para un lavador
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.services import WashingService as WashingServiceModel
from app.infrastructure.database.models.users import Washer, OperationalAdmin
from app.infrastructure.database.models.vehicles import Vehicle
from app.infrastructure.database.models.financial import Shift

async def create_test_services():
    async with SessionLocal() as session:
        # Obtener el lavador
        result = await session.execute(
            select(Washer).where(Washer.id == 1)
        )
        washer = result.scalar_one_or_none()
        
        if not washer:
            print("❌ Washer not found")
            return
        
        # Obtener un vehículo
        result = await session.execute(select(Vehicle).limit(1))
        vehicle = result.scalar_one_or_none()
        
        if not vehicle:
            print("❌ No vehicles found in database")
            return
        
        # Obtener o crear un turno para el admin operacional
        result = await session.execute(
            select(OperationalAdmin).limit(1)
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("❌ No operational admin found")
            return
        
        # Obtener turno activo o crear uno
        now = datetime.now(timezone.utc)
        result = await session.execute(
            select(Shift).where(
                (Shift.admin_id == admin.id) & (Shift.end_time.is_(None))
            ).limit(1)
        )
        shift = result.scalar_one_or_none()
        
        if not shift:
            shift = Shift(
                admin_id=admin.id,
                shift_date=now.date(),
                start_time=now,
                initial_cash=0
            )
            session.add(shift)
            await session.flush()
            print(f"✅ Created new shift for admin {admin.id}")
        
        print(f"✅ Creating services for washer: {washer.email}")
        print(f"✅ Using vehicle: {vehicle.plate}")
        print(f"✅ Using shift: {shift.id}")
        print(f"✅ Using admin: {admin.id}")
        
        # Crear 3 servicios nuevos con diferentes estados
        
        # 1. Servicio pendiente (sin start_time ni end_time)
        service1 = WashingServiceModel(
            vehicle_id=vehicle.id,
            washer_id=washer.id,
            admin_id=admin.id,
            shift_id=shift.id,
            service_type="basic",
            price=30000,
            service_date=now.date(),
            payment_status="pending"
        )
        
        # 2. Servicio en progreso (con start_time pero sin end_time)
        service2 = WashingServiceModel(
            vehicle_id=vehicle.id,
            washer_id=washer.id,
            admin_id=admin.id,
            shift_id=shift.id,
            service_type="deluxe",
            price=60000,
            service_date=now.date(),
            start_time=now,
            payment_status="pending"
        )
        
        # 3. Servicio completado (con start_time y end_time)
        service3 = WashingServiceModel(
            vehicle_id=vehicle.id,
            washer_id=washer.id,
            admin_id=admin.id,
            shift_id=shift.id,
            service_type="premium",
            price=80000,
            service_date=now.date(),
            start_time=now,
            end_time=now,
            payment_status="paid"
        )
        
        session.add(service1)
        session.add(service2)
        session.add(service3)
        
        await session.commit()
        
        print("✅ Created 3 test services:")
        print("  1. Pending (estado: pending)")
        print("  2. In Progress (estado: in_progress)")
        print("  3. Completed (estado: completed)")

if __name__ == "__main__":
    asyncio.run(create_test_services())
