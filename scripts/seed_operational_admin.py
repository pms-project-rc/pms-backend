import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import OperationalAdmin
from app.core.security import get_password_hash
from sqlalchemy import select

async def seed_op_admin():
    async with SessionLocal() as session:
        # Check if exists
        result = await session.execute(select(OperationalAdmin).where(OperationalAdmin.email == "op@pms.com"))
        admin = result.scalar_one_or_none()
        if admin:
            print("Operational Admin already exists. Updating password...")
            admin.password_hash = get_password_hash("op123")
            session.add(admin)
            await session.commit()
            print("Operational Admin password updated: op@pms.com / op123")
            return

        admin = OperationalAdmin(
            email="op@pms.com",
            full_name="Operational Admin",
            password_hash=get_password_hash("op123"),
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("Operational Admin created: op@pms.com / op123")

if __name__ == "__main__":
    asyncio.run(seed_op_admin())
