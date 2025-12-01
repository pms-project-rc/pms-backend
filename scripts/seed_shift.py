import asyncio
import os
import sys
from datetime import datetime, date

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.financial import Shift
from app.infrastructure.database.models.users import OperationalAdmin
from sqlalchemy import select

async def seed_shift():
    async with SessionLocal() as session:
        # Get the first operational admin
        result = await session.execute(select(OperationalAdmin).limit(1))
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("❌ No operational admin found. Please create one first using seed_operational_admin.py")
            return
        
        # Check if a shift already exists for today
        today = date.today()
        result = await session.execute(
            select(Shift)
            .where(Shift.admin_id == admin.id)
            .where(Shift.shift_date == today)
            .where(Shift.end_time.is_(None))
        )
        existing_shift = result.scalar_one_or_none()
        
        if existing_shift:
            print(f"✓ Active shift already exists for {admin.full_name} (ID: {existing_shift.id})")
            print(f"  Shift Date: {existing_shift.shift_date}")
            print(f"  Start Time: {existing_shift.start_time}")
            return
        
        # Create a new shift
        shift = Shift(
            admin_id=admin.id,
            shift_date=today,
            start_time=datetime.now(),
            end_time=None,  # Shift is still active
            initial_cash=0,
            final_cash=None,
            total_income=0,
            total_expenses=0,
            notes="Turno de ejemplo creado automáticamente"
        )
        
        session.add(shift)
        await session.commit()
        await session.refresh(shift)
        
        print(f"✓ Shift created successfully!")
        print(f"  Shift ID: {shift.id}")
        print(f"  Admin: {admin.full_name}")
        print(f"  Date: {shift.shift_date}")
        print(f"  Start Time: {shift.start_time}")

if __name__ == "__main__":
    asyncio.run(seed_shift())
