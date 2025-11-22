"""
Casos de uso para la gestión de Operational Admins.
"""
from typing import Optional, List
from datetime import datetime
from app.domain.users.entities import OperationalAdmin
from app.domain.users.repositories import OperationalAdminRepository
from app.domain.users.events import UserCreatedEvent, UserUpdatedEvent


class CreateOperationalAdminUseCase:
    """Caso de uso para crear un nuevo Operational Admin."""
    
    def __init__(self, repository: OperationalAdminRepository):
        self.repository = repository
    
    async def execute(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        phone: Optional[str] = None
    ) -> OperationalAdmin:
        """
        Crea un nuevo Operational Admin.
        
        Args:
            email: Email del administrador
            password_hash: Hash de la contraseña
            full_name: Nombre completo
            phone: Teléfono (opcional)
            
        Returns:
            El Operational Admin creado
            
        Raises:
            ValueError: Si el email ya existe
        """
        # Verificar que no exista un admin con ese email
        existing = await self.repository.find_by_email(email)
        if existing:
            raise ValueError(f"Ya existe un administrador con el email: {email}")
        
        # Crear la entidad
        admin = OperationalAdmin(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Guardar en el repositorio
        saved_admin = await self.repository.save(admin)
        
        return saved_admin


class GetOperationalAdminByIdUseCase:
    """Caso de uso para obtener un Operational Admin por ID."""
    
    def __init__(self, repository: OperationalAdminRepository):
        self.repository = repository
    
    async def execute(self, admin_id: int) -> Optional[OperationalAdmin]:
        """Obtiene un Operational Admin por su ID."""
        return await self.repository.find_by_id(admin_id)


class GetOperationalAdminByEmailUseCase:
    """Caso de uso para obtener un Operational Admin por email."""
    
    def __init__(self, repository: OperationalAdminRepository):
        self.repository = repository
    
    async def execute(self, email: str) -> Optional[OperationalAdmin]:
        """Obtiene un Operational Admin por su email."""
        return await self.repository.find_by_email(email)


class ListOperationalAdminsUseCase:
    """Caso de uso para listar Operational Admins."""
    
    def __init__(self, repository: OperationalAdminRepository):
        self.repository = repository
    
    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = False
    ) -> List[OperationalAdmin]:
        """Lista los Operational Admins con paginación."""
        if only_active:
            return await self.repository.find_active()
        return await self.repository.find_all(skip=skip, limit=limit)


class UpdateOperationalAdminUseCase:
    """Caso de uso para actualizar un Operational Admin."""
    
    def __init__(self, repository: OperationalAdminRepository):
        self.repository = repository
    
    async def execute(
        self,
        admin_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[OperationalAdmin]:
        """Actualiza un Operational Admin."""
        admin = await self.repository.find_by_id(admin_id)
        if not admin:
            return None
        
        if full_name is not None:
            admin.full_name = full_name
        if phone is not None:
            admin.phone = phone
        if is_active is not None:
            if is_active:
                admin.activate()
            else:
                admin.deactivate()
        
        admin.updated_at = datetime.now()
        
        return await self.repository.save(admin)


class DeleteOperationalAdminUseCase:
    """Caso de uso para eliminar un Operational Admin."""
    
    def __init__(self, repository: OperationalAdminRepository):
        self.repository = repository
    
    async def execute(self, admin_id: int) -> bool:
        """Elimina un Operational Admin."""
        return await self.repository.delete(admin_id)
