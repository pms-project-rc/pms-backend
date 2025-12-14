from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.sql import func
from app.domain.users.entities.global_admin import GlobalAdmin
from app.domain.users.repositories.global_admin_repository import IGlobalAdminRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import GlobalAdmin as GlobalAdminModel

class GlobalAdminRepositoryImpl(IGlobalAdminRepository):
    
    def _to_entity(self, model: GlobalAdminModel) -> Optional[GlobalAdmin]:
        if not model:
            return None
        return GlobalAdmin(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            password_hash=model.password_hash,
            is_active=model.is_active,
            last_login=model.last_login,
            phone=model.phone
        )

    async def get_by_email(self, email: str) -> Optional[GlobalAdmin]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(GlobalAdminModel).where(GlobalAdminModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def get_by_id(self, admin_id: int) -> Optional[GlobalAdmin]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(GlobalAdminModel).where(GlobalAdminModel.id == admin_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def update_last_login(self, admin_id: int) -> None:
        async with SessionLocal() as session:
            await session.execute(
                update(GlobalAdminModel)
                .where(GlobalAdminModel.id == admin_id)
                .values(last_login=func.now())
            )
            await session.commit()

    async def update_password(self, admin_id: int, new_password_hash: str) -> None:
        async with SessionLocal() as session:
            await session.execute(
                update(GlobalAdminModel)
                .where(GlobalAdminModel.id == admin_id)
                .values(password_hash=new_password_hash)
            )
            await session.commit()
    
    async def get_all(self):
        """Obtiene todos los administradores globales."""
        async with SessionLocal() as session:
            result = await session.execute(select(GlobalAdminModel))
            models = result.scalars().all()
            return [GlobalAdminModel(
                id=m.id,
                email=m.email,
                full_name=m.full_name,
                phone=m.phone,
                is_active=m.is_active,
                created_at=m.created_at,
                password_hash=m.password_hash
            ) for m in models]
    
    async def create(self, email: str, password_hash: str, full_name: str, phone: Optional[str] = None):
        """Crea un nuevo administrador global."""
        async with SessionLocal() as session:
            model = GlobalAdminModel(
                email=email,
                password_hash=password_hash,
                full_name=full_name,
                phone=phone
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return model
    
    async def update(self, admin_id: int, admin: GlobalAdmin) -> GlobalAdmin:
        """Actualiza un administrador global."""
        async with SessionLocal() as session:
            stmt = (
                update(GlobalAdminModel)
                .where(GlobalAdminModel.id == admin_id)
                .values(
                    full_name=admin.full_name,
                    email=admin.email,
                    phone=admin.phone,
                    is_active=admin.is_active,
                    password_hash=admin.password_hash
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            result = await session.execute(
                select(GlobalAdminModel).where(GlobalAdminModel.id == admin_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def delete(self, admin_id: int) -> bool:
        """Elimina un administrador global."""
        async with SessionLocal() as session:
            result = await session.execute(
                select(GlobalAdminModel).where(GlobalAdminModel.id == admin_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

