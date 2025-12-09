import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from sqlalchemy import text

async def show_table_structure():
    async with SessionLocal() as session:
        # Show operational_admins structure
        result = await session.execute(text("SELECT * FROM operational_admins LIMIT 1"))
        if result.keys():
            print("=== OPERATIONAL_ADMINS COLUMNS ===")
            for col in result.keys():
                print(f"  - {col}")
        
        # Show actual data
        result = await session.execute(text("SELECT * FROM operational_admins"))
        rows = result.fetchall()
        print(f"\n=== OPERATIONAL_ADMINS DATA ({len(rows)} rows) ===")
        for row in rows:
            print(dict(row._mapping))

if __name__ == "__main__":
    asyncio.run(show_table_structure())
