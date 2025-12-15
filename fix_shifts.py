import asyncio
import sys
import os
from datetime import datetime

# Ensure /app is in path
sys.path.append('/app')

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.financial import Shift
from sqlalchemy import select, func, update

async def fix_shifts():
    async with SessionLocal() as session:
        print("Fixing duplicate active shifts...")
        
        # Find admins with multiple active shifts
        result = await session.execute(
            select(Shift.admin_id, func.count(Shift.id))
            .where(Shift.end_time.is_(None))
            .group_by(Shift.admin_id)
            .having(func.count(Shift.id) > 1)
        )
        duplicates = result.all()
        
        for admin_id, count in duplicates:
            print(f"Processing Admin ID: {admin_id} with {count} active shifts")
            
            # Get all active shifts for this admin, ordered by ID desc
            shifts_result = await session.execute(
                select(Shift)
                .where(Shift.admin_id == admin_id)
                .where(Shift.end_time.is_(None))
                .order_by(Shift.id.desc())
            )
            shifts = shifts_result.scalars().all()
            
            # Keep the first one (most recent), close the rest
            most_recent = shifts[0]
            others = shifts[1:]
            
            print(f"Keeping Shift ID: {most_recent.id} active.")
            
            for shift in others:
                print(f"Closing Shift ID: {shift.id}...")
                shift.end_time = datetime.now()
                shift.notes = (shift.notes or "") + " [System: Closed duplicate shift]"
                # We might want to set final_cash = initial_cash if we assume no activity
                if shift.final_cash is None:
                    shift.final_cash = shift.initial_cash
                
                session.add(shift)
            
        await session.commit()
        print("Duplicate shifts closed successfully.")

if __name__ == "__main__":
    asyncio.run(fix_shifts())
