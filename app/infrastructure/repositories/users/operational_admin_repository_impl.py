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
