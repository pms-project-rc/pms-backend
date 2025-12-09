import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.infrastructure.database.session import SessionLocal
from sqlalchemy import text

async def show_table_structure():
    async with SessionLocal() as session:
        # Show washers structure
        result = await session.execute(text("SELECT * FROM washers LIMIT 1"))
        if result.keys():
            print("=== WASHERS COLUMNS ===")
            for col in result.keys():
                print(f"  - {col}")
        
        # Show actual data
        result = await session.execute(text("SELECT * FROM washers"))
        rows = result.fetchall()
        print(f"\n=== WASHERS DATA ({len(rows)} rows) ===")
        for row in rows:
            print(dict(row._mapping))

if __name__ == "__main__":
    asyncio.run(show_table_structure())
