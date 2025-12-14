from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.sql import func
from app.domain.users.entities.operational_admin import OperationalAdmin
from app.domain.users.repositories.operational_admin_repository import IOperationalAdminRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import OperationalAdmin as OperationalAdminModel

class OperationalAdminRepositoryImpl(IOperationalAdminRepository):
    
    def _to_entity(self, model: OperationalAdminModel) -> Optional[OperationalAdmin]:
        if not model:
            return None
        return OperationalAdmin(
            id=model.id,
            email=model.email,
            full_name=model.full_name,
            password_hash=model.password_hash,
            is_active=model.is_active,
            last_login=model.last_login,
            phone=model.phone
        )

    def _to_model(self, entity: OperationalAdmin) -> OperationalAdminModel:
        return OperationalAdminModel(
            id=entity.id,
            email=entity.email,
            full_name=entity.full_name,
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            last_login=entity.last_login,
            phone=entity.phone
        )

    async def get_by_email(self, email: str) -> Optional[OperationalAdmin]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(OperationalAdminModel).where(OperationalAdminModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def get_by_id(self, admin_id: int) -> Optional[OperationalAdmin]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(OperationalAdminModel).where(OperationalAdminModel.id == admin_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def create(self, admin: OperationalAdmin) -> OperationalAdmin:
        async with SessionLocal() as session:
            model = self._to_model(admin)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def update_last_login(self, admin_id: int) -> None:
        async with SessionLocal() as session:
            await session.execute(
                update(OperationalAdminModel)
                .where(OperationalAdminModel.id == admin_id)
                .values(last_login=func.now())
            )
            await session.commit()
    
    async def get_all(self):
        """Obtiene todos los administradores operacionales."""
        async with SessionLocal() as session:
            result = await session.execute(select(OperationalAdminModel))
            models = result.scalars().all()
            return [OperationalAdminModel(
                id=m.id,
                email=m.email,
                full_name=m.full_name,
                phone=m.phone,
                is_active=m.is_active,
                created_at=m.created_at,
                password_hash=m.password_hash
            ) for m in models]
    
    async def update(self, admin_id: int, admin: OperationalAdmin) -> OperationalAdmin:
        """Actualiza un administrador operacional."""
        async with SessionLocal() as session:
            stmt = (
                update(OperationalAdminModel)
                .where(OperationalAdminModel.id == admin_id)
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
                select(OperationalAdminModel).where(OperationalAdminModel.id == admin_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def delete(self, admin_id: int) -> bool:
        """Elimina un administrador operacional."""
        async with SessionLocal() as session:
            result = await session.execute(
                select(OperationalAdminModel).where(OperationalAdminModel.id == admin_id)
            )
            model = result.scalar_one_or_none()
            if model:
                await session.delete(model)
                await session.commit()
                return True
            return False

