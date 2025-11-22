"""
Dependencias para la API - Inyección de dependencias.

Este módulo provee las funciones de dependencia para FastAPI,
incluyendo sesiones de base de datos y repositorios.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

# Crear el engine async
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True
)

# Crear el session maker
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia para obtener una sesión de base de datos.
    
    Yields:
        AsyncSession: Sesión de base de datos async
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
