from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl
from app.infrastructure.repositories.users.operational_admin_repository_impl import OperationalAdminRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.application.dto.users.employee_create_request import EmployeeCreateRequest
from app.application.dto.users.employee_response import EmployeeResponse
from app.core.security import get_password_hash
from fastapi import HTTPException


class CreateEmployee:
    """Caso de uso para crear un nuevo empleado."""
    
    def __init__(
        self,
        global_admin_repo: GlobalAdminRepositoryImpl,
        operational_admin_repo: OperationalAdminRepositoryImpl,
        washer_repo: WasherRepositoryImpl
    ):
        self.global_admin_repo = global_admin_repo
        self.operational_admin_repo = operational_admin_repo
        self.washer_repo = washer_repo
    
    async def execute(self, data: EmployeeCreateRequest) -> EmployeeResponse:
        """
        Ejecuta el caso de uso para crear un empleado.
        
        Args:
            data: Datos del empleado a crear.
            
        Returns:
            EmployeeResponse: Empleado creado.
            
        Raises:
            HTTPException: Si el email ya existe.
        """
        # Verificar que el email no exista en ninguna tabla
        if await self._email_exists(data.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Hash de la contraseña
        password_hash = get_password_hash(data.password)
        
        # Crear según el rol
        if data.role == 'global_admin':
            from app.domain.users.entities.global_admin import GlobalAdmin
            from app.infrastructure.database.models.users import GlobalAdmin as GlobalAdminModel
            from app.infrastructure.database.session import SessionLocal
            
            # Crear directamente en la base de datos
            async with SessionLocal() as session:
                model = GlobalAdminModel(
                    email=data.email,
                    password_hash=password_hash,
                    full_name=data.full_name,
                    phone=data.phone
                )
                session.add(model)
                await session.commit()
                await session.refresh(model)
                
                return EmployeeResponse(
                    id=model.id,
                    full_name=model.full_name,
                    email=model.email,
                    phone=model.phone,
                    role='global_admin',
                    is_active=model.is_active,
                    created_at=model.created_at,
                    commission_percentage=None
                )
        
        elif data.role == 'operational_admin':
            from app.domain.users.entities.operational_admin import OperationalAdmin
            from app.infrastructure.database.models.users import OperationalAdmin as OperationalAdminModel
            from app.infrastructure.database.session import SessionLocal
            
            # Crear directamente en la base de datos
            async with SessionLocal() as session:
                model = OperationalAdminModel(
                    email=data.email,
                    password_hash=password_hash,
                    full_name=data.full_name,
                    phone=data.phone
                )
                session.add(model)
                await session.commit()
                await session.refresh(model)
                
                return EmployeeResponse(
                    id=model.id,
                    full_name=model.full_name,
                    email=model.email,
                    phone=model.phone,
                    role='operational_admin',
                    is_active=model.is_active,
                    created_at=model.created_at,
                    commission_percentage=None
                )
        
        elif data.role == 'washer':
            from app.domain.washers.entities.washer import Washer
            from app.infrastructure.database.models.users import Washer as WasherModel
            from app.infrastructure.database.session import SessionLocal
            
            # Crear directamente en la base de datos
            async with SessionLocal() as session:
                model = WasherModel(
                    email=data.email,
                    password_hash=password_hash,
                    full_name=data.full_name,
                    phone=data.phone,
                    commission_percentage=data.commission_percentage or 0
                )
                session.add(model)
                await session.commit()
                await session.refresh(model)
                
                return EmployeeResponse(
                    id=model.id,
                    full_name=model.full_name,
                    email=model.email,
                    phone=model.phone,
                    role='washer',
                    is_active=model.is_active,
                    created_at=model.created_at,
                    commission_percentage=model.commission_percentage
                )
        
        raise HTTPException(status_code=400, detail="Invalid role")
    
    async def _email_exists(self, email: str) -> bool:
        """Verifica si un email ya existe en el sistema."""
        if await self.global_admin_repo.get_by_email(email):
            return True
        if await self.operational_admin_repo.get_by_email(email):
            return True
        if await self.washer_repo.get_by_email(email):
            return True
        return False
