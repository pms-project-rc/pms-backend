import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import GlobalAdmin
from app.core.security import get_password_hash
from sqlalchemy import select

async def seed_custom_admin():
    async with SessionLocal() as session:
        # Check if exists
        result = await session.execute(select(GlobalAdmin).where(GlobalAdmin.email == "administrador@pms.com"))
        admin = result.scalar_one_or_none()
        if admin:
            print("Administrador already exists. Updating password...")
            admin.password_hash = get_password_hash("123456")
            session.add(admin)
            await session.commit()
            print("Administrador password updated: administrador@pms.com / 123456")
            return

        admin = GlobalAdmin(
            email="administrador@pms.com",
            full_name="Administrador General",
            password_hash=get_password_hash("123456"),
            is_active=True
        )
        session.add(admin)
        await session.commit()
        print("Administrador created: administrador@pms.com / 123456")

if __name__ == "__main__":
    asyncio.run(seed_custom_admin())
