"""
Casos de uso para la gestión de Global Admins.

Los casos de uso orquestan las operaciones del dominio
y las reglas de negocio de la aplicación.
"""
from typing import Optional, List
from datetime import datetime
from app.domain.users.entities import GlobalAdmin
from app.domain.users.repositories import GlobalAdminRepository
from app.domain.users.events import UserCreatedEvent, UserUpdatedEvent


class CreateGlobalAdminUseCase:
    """
    Caso de uso para crear un nuevo Global Admin.
    
    Attributes:
        repository: Repositorio de Global Admins
    """
    
    def __init__(self, repository: GlobalAdminRepository):
        self.repository = repository
    
    async def execute(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        phone: Optional[str] = None
    ) -> GlobalAdmin:
        """
        Crea un nuevo Global Admin.
        
        Args:
            email: Email del administrador
            password_hash: Hash de la contraseña
            full_name: Nombre completo
            phone: Teléfono (opcional)
            
        Returns:
            El Global Admin creado
            
        Raises:
            ValueError: Si el email ya existe
        """
        # Verificar que no exista un admin con ese email
        existing = await self.repository.find_by_email(email)
        if existing:
            raise ValueError(f"Ya existe un administrador con el email: {email}")
        
        # Crear la entidad
        admin = GlobalAdmin(
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
        
        # TODO: Emitir evento de dominio
        # event = UserCreatedEvent(saved_admin.id, "global_admin", email)
        
        return saved_admin


class GetGlobalAdminByIdUseCase:
    """Caso de uso para obtener un Global Admin por ID."""
    
    def __init__(self, repository: GlobalAdminRepository):
        self.repository = repository
    
    async def execute(self, admin_id: int) -> Optional[GlobalAdmin]:
        """
        Obtiene un Global Admin por su ID.
        
        Args:
            admin_id: ID del administrador
            
        Returns:
            El Global Admin si existe, None si no
        """
        return await self.repository.find_by_id(admin_id)


class GetGlobalAdminByEmailUseCase:
    """Caso de uso para obtener un Global Admin por email."""
    
    def __init__(self, repository: GlobalAdminRepository):
        self.repository = repository
    
    async def execute(self, email: str) -> Optional[GlobalAdmin]:
        """
        Obtiene un Global Admin por su email.
        
        Args:
            email: Email del administrador
            
        Returns:
            El Global Admin si existe, None si no
        """
        return await self.repository.find_by_email(email)


class ListGlobalAdminsUseCase:
    """Caso de uso para listar Global Admins con paginación."""
    
    def __init__(self, repository: GlobalAdminRepository):
        self.repository = repository
    
    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = False
    ) -> List[GlobalAdmin]:
        """
        Lista los Global Admins con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            only_active: Si True, solo retorna administradores activos
            
        Returns:
            Lista de Global Admins
        """
        if only_active:
            return await self.repository.find_active()
        return await self.repository.find_all(skip=skip, limit=limit)


class UpdateGlobalAdminUseCase:
    """Caso de uso para actualizar un Global Admin."""
    
    def __init__(self, repository: GlobalAdminRepository):
        self.repository = repository
    
    async def execute(
        self,
        admin_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> Optional[GlobalAdmin]:
        """
        Actualiza un Global Admin.
        
        Args:
            admin_id: ID del administrador
            full_name: Nuevo nombre completo (opcional)
            phone: Nuevo teléfono (opcional)
            is_active: Nuevo estado (opcional)
            
        Returns:
            El Global Admin actualizado, None si no existe
        """
        # Buscar el admin
        admin = await self.repository.find_by_id(admin_id)
        if not admin:
            return None
        
        # Actualizar campos
        changes = {}
        if full_name is not None:
            admin.full_name = full_name
            changes["full_name"] = full_name
        if phone is not None:
            admin.phone = phone
            changes["phone"] = phone
        if is_active is not None:
            if is_active:
                admin.activate()
            else:
                admin.deactivate()
            changes["is_active"] = is_active
        
        admin.updated_at = datetime.now()
        
        # Guardar cambios
        updated_admin = await self.repository.save(admin)
        
        # TODO: Emitir evento de dominio
        # event = UserUpdatedEvent(admin_id, "global_admin", changes)
        
        return updated_admin


class DeleteGlobalAdminUseCase:
    """Caso de uso para eliminar un Global Admin."""
    
    def __init__(self, repository: GlobalAdminRepository):
        self.repository = repository
    
    async def execute(self, admin_id: int) -> bool:
        """
        Elimina un Global Admin.
        
        Args:
            admin_id: ID del administrador a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        # TODO: Agregar validación de negocio
        # Por ejemplo, no permitir eliminar el último Global Admin
        
        result = await self.repository.delete(admin_id)
        
        # TODO: Emitir evento de dominio
        # if result:
        #     event = UserDeletedEvent(admin_id, "global_admin")
        
        return result
