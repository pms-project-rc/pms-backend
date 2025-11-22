"""
Implementación de repositorios SQLAlchemy para usuarios.

Estos adapters implementan las interfaces definidas en la capa de dominio
y conectan las entidades de dominio con los modelos de SQLAlchemy.
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.domain.users.entities import GlobalAdmin, OperationalAdmin, Washer
from app.domain.users.repositories import (
    GlobalAdminRepository,
    OperationalAdminRepository,
    WasherRepository
)
from app.infrastructure.database.models.users import (
    GlobalAdmin as GlobalAdminModel,
    OperationalAdmin as OperationalAdminModel,
    Washer as WasherModel
)


class SQLAlchemyGlobalAdminRepository(GlobalAdminRepository):
    """
    Implementación de repositorio para Global Admins usando SQLAlchemy.
    
    Attributes:
        session: Sesión de base de datos async
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: GlobalAdminModel) -> GlobalAdmin:
        """Convierte un modelo SQLAlchemy en entidad de dominio."""
        return GlobalAdmin(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            phone=model.phone,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )
    
    def _to_model(self, entity: GlobalAdmin) -> GlobalAdminModel:
        """Convierte una entidad de dominio en modelo SQLAlchemy."""
        return GlobalAdminModel(
            id=entity.id,
            email=entity.email,
            password_hash=entity.password_hash,
            full_name=entity.full_name,
            phone=entity.phone,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            last_login=entity.last_login
        )
    
    async def save(self, admin: GlobalAdmin) -> GlobalAdmin:
        """Guarda o actualiza un Global Admin."""
        if admin.id:
            # Actualizar existente
            stmt = select(GlobalAdminModel).where(GlobalAdminModel.id == admin.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                model.email = admin.email
                model.password_hash = admin.password_hash
                model.full_name = admin.full_name
                model.phone = admin.phone
                model.is_active = admin.is_active
                model.updated_at = admin.updated_at
                model.last_login = admin.last_login
            else:
                raise ValueError(f"Global Admin con ID {admin.id} no encontrado")
        else:
            # Crear nuevo
            model = self._to_model(admin)
            self.session.add(model)
        
        try:
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Error de integridad: {str(e)}")
    
    async def find_by_id(self, user_id: int) -> Optional[GlobalAdmin]:
        """Busca un Global Admin por ID."""
        stmt = select(GlobalAdminModel).where(GlobalAdminModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_by_email(self, email: str) -> Optional[GlobalAdmin]:
        """Busca un Global Admin por email."""
        stmt = select(GlobalAdminModel).where(GlobalAdminModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[GlobalAdmin]:
        """Obtiene todos los Global Admins con paginación."""
        stmt = select(GlobalAdminModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def find_active(self) -> List[GlobalAdmin]:
        """Obtiene todos los Global Admins activos."""
        stmt = select(GlobalAdminModel).where(GlobalAdminModel.is_active == True)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def delete(self, user_id: int) -> bool:
        """Elimina un Global Admin."""
        stmt = select(GlobalAdminModel).where(GlobalAdminModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False


class SQLAlchemyOperationalAdminRepository(OperationalAdminRepository):
    """Implementación de repositorio para Operational Admins usando SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: OperationalAdminModel) -> OperationalAdmin:
        """Convierte un modelo SQLAlchemy en entidad de dominio."""
        return OperationalAdmin(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            phone=model.phone,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )
    
    async def save(self, admin: OperationalAdmin) -> OperationalAdmin:
        """Guarda o actualiza un Operational Admin."""
        if admin.id:
            stmt = select(OperationalAdminModel).where(OperationalAdminModel.id == admin.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                model.email = admin.email
                model.password_hash = admin.password_hash
                model.full_name = admin.full_name
                model.phone = admin.phone
                model.is_active = admin.is_active
                model.updated_at = admin.updated_at
                model.last_login = admin.last_login
            else:
                raise ValueError(f"Operational Admin con ID {admin.id} no encontrado")
        else:
            model = OperationalAdminModel(
                email=admin.email,
                password_hash=admin.password_hash,
                full_name=admin.full_name,
                phone=admin.phone,
                is_active=admin.is_active,
                created_at=admin.created_at,
                updated_at=admin.updated_at,
                last_login=admin.last_login
            )
            self.session.add(model)
        
        try:
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Error de integridad: {str(e)}")
    
    async def find_by_id(self, user_id: int) -> Optional[OperationalAdmin]:
        """Busca un Operational Admin por ID."""
        stmt = select(OperationalAdminModel).where(OperationalAdminModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_by_email(self, email: str) -> Optional[OperationalAdmin]:
        """Busca un Operational Admin por email."""
        stmt = select(OperationalAdminModel).where(OperationalAdminModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[OperationalAdmin]:
        """Obtiene todos los Operational Admins con paginación."""
        stmt = select(OperationalAdminModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def find_active(self) -> List[OperationalAdmin]:
        """Obtiene todos los Operational Admins activos."""
        stmt = select(OperationalAdminModel).where(OperationalAdminModel.is_active == True)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def delete(self, user_id: int) -> bool:
        """Elimina un Operational Admin."""
        stmt = select(OperationalAdminModel).where(OperationalAdminModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False


class SQLAlchemyWasherRepository(WasherRepository):
    """Implementación de repositorio para Washers usando SQLAlchemy."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    def _to_entity(self, model: WasherModel) -> Washer:
        """Convierte un modelo SQLAlchemy en entidad de dominio."""
        return Washer(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            full_name=model.full_name,
            phone=model.phone,
            commission_percentage=model.commission_percentage,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
            last_login=model.last_login
        )
    
    async def save(self, washer: Washer) -> Washer:
        """Guarda o actualiza un Washer."""
        if washer.id:
            stmt = select(WasherModel).where(WasherModel.id == washer.id)
            result = await self.session.execute(stmt)
            model = result.scalar_one_or_none()
            
            if model:
                model.email = washer.email
                model.password_hash = washer.password_hash
                model.full_name = washer.full_name
                model.phone = washer.phone
                model.commission_percentage = washer.commission_percentage
                model.is_active = washer.is_active
                model.updated_at = washer.updated_at
                model.last_login = washer.last_login
            else:
                raise ValueError(f"Washer con ID {washer.id} no encontrado")
        else:
            model = WasherModel(
                email=washer.email,
                password_hash=washer.password_hash,
                full_name=washer.full_name,
                phone=washer.phone,
                commission_percentage=washer.commission_percentage,
                is_active=washer.is_active,
                created_at=washer.created_at,
                updated_at=washer.updated_at,
                last_login=washer.last_login
            )
            self.session.add(model)
        
        try:
            await self.session.commit()
            await self.session.refresh(model)
            return self._to_entity(model)
        except IntegrityError as e:
            await self.session.rollback()
            raise ValueError(f"Error de integridad: {str(e)}")
    
    async def find_by_id(self, user_id: int) -> Optional[Washer]:
        """Busca un Washer por ID."""
        stmt = select(WasherModel).where(WasherModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_by_email(self, email: str) -> Optional[Washer]:
        """Busca un Washer por email."""
        stmt = select(WasherModel).where(WasherModel.email == email)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None
    
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Washer]:
        """Obtiene todos los Washers con paginación."""
        stmt = select(WasherModel).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def find_active(self) -> List[Washer]:
        """Obtiene todos los Washers activos."""
        stmt = select(WasherModel).where(WasherModel.is_active == True)
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def find_by_commission_range(
        self,
        min_commission: int,
        max_commission: int
    ) -> List[Washer]:
        """Busca lavadores por rango de comisión."""
        stmt = select(WasherModel).where(
            WasherModel.commission_percentage >= min_commission,
            WasherModel.commission_percentage <= max_commission
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
    
    async def delete(self, user_id: int) -> bool:
        """Elimina un Washer."""
        stmt = select(WasherModel).where(WasherModel.id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()
        
        if model:
            await self.session.delete(model)
            await self.session.commit()
            return True
        return False
