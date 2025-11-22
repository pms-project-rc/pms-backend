"""
Casos de uso para la gestión de Washers (Lavadores).
"""
from typing import Optional, List
from datetime import datetime
from app.domain.users.entities import Washer
from app.domain.users.repositories import WasherRepository
from app.domain.users.events import UserCreatedEvent, UserUpdatedEvent


class CreateWasherUseCase:
    """Caso de uso para crear un nuevo Washer."""
    
    def __init__(self, repository: WasherRepository):
        self.repository = repository
    
    async def execute(
        self,
        email: str,
        password_hash: str,
        full_name: str,
        phone: Optional[str] = None,
        commission_percentage: int = 0
    ) -> Washer:
        """
        Crea un nuevo Washer.
        
        Args:
            email: Email del lavador
            password_hash: Hash de la contraseña
            full_name: Nombre completo
            phone: Teléfono (opcional)
            commission_percentage: Porcentaje de comisión (0-100)
            
        Returns:
            El Washer creado
            
        Raises:
            ValueError: Si el email ya existe o la comisión es inválida
        """
        # Verificar que no exista un washer con ese email
        existing = await self.repository.find_by_email(email)
        if existing:
            raise ValueError(f"Ya existe un lavador con el email: {email}")
        
        # Crear la entidad (validará automáticamente la comisión)
        washer = Washer(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            phone=phone,
            commission_percentage=commission_percentage,
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Guardar en el repositorio
        saved_washer = await self.repository.save(washer)
        
        return saved_washer


class GetWasherByIdUseCase:
    """Caso de uso para obtener un Washer por ID."""
    
    def __init__(self, repository: WasherRepository):
        self.repository = repository
    
    async def execute(self, washer_id: int) -> Optional[Washer]:
        """Obtiene un Washer por su ID."""
        return await self.repository.find_by_id(washer_id)


class GetWasherByEmailUseCase:
    """Caso de uso para obtener un Washer por email."""
    
    def __init__(self, repository: WasherRepository):
        self.repository = repository
    
    async def execute(self, email: str) -> Optional[Washer]:
        """Obtiene un Washer por su email."""
        return await self.repository.find_by_email(email)


class ListWashersUseCase:
    """Caso de uso para listar Washers."""
    
    def __init__(self, repository: WasherRepository):
        self.repository = repository
    
    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        only_active: bool = False
    ) -> List[Washer]:
        """Lista los Washers con paginación."""
        if only_active:
            return await self.repository.find_active()
        return await self.repository.find_all(skip=skip, limit=limit)


class UpdateWasherUseCase:
    """Caso de uso para actualizar un Washer."""
    
    def __init__(self, repository: WasherRepository):
        self.repository = repository
    
    async def execute(
        self,
        washer_id: int,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        commission_percentage: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> Optional[Washer]:
        """
        Actualiza un Washer.
        
        Args:
            washer_id: ID del lavador
            full_name: Nuevo nombre completo (opcional)
            phone: Nuevo teléfono (opcional)
            commission_percentage: Nuevo porcentaje de comisión (opcional)
            is_active: Nuevo estado (opcional)
            
        Returns:
            El Washer actualizado, None si no existe
        """
        washer = await self.repository.find_by_id(washer_id)
        if not washer:
            return None
        
        if full_name is not None:
            washer.full_name = full_name
        if phone is not None:
            washer.phone = phone
        if commission_percentage is not None:
            # Usa el método de dominio que valida
            washer.set_commission_percentage(commission_percentage)
        if is_active is not None:
            if is_active:
                washer.activate()
            else:
                washer.deactivate()
        
        washer.updated_at = datetime.now()
        
        return await self.repository.save(washer)


class DeleteWasherUseCase:
    """Caso de uso para eliminar un Washer."""
    
    def __init__(self, repository: WasherRepository):
        self.repository = repository
    
    async def execute(self, washer_id: int) -> bool:
        """
        Elimina un Washer.
        
        Args:
            washer_id: ID del lavador a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        # TODO: Validar que no tenga servicios pendientes
        return await self.repository.delete(washer_id)


class GetWashersByCommissionRangeUseCase:
    """Caso de uso para buscar lavadores por rango de comisión."""
    
    def __init__(self, repository: WasherRepository):
        self.repository = repository
    
    async def execute(
        self,
        min_commission: int,
        max_commission: int
    ) -> List[Washer]:
        """
        Busca lavadores por rango de comisión.
        
        Args:
            min_commission: Porcentaje mínimo de comisión
            max_commission: Porcentaje máximo de comisión
            
        Returns:
            Lista de lavadores en el rango especificado
        """
        if not (0 <= min_commission <= 100) or not (0 <= max_commission <= 100):
            raise ValueError("Los porcentajes deben estar entre 0 y 100")
        if min_commission > max_commission:
            raise ValueError("El porcentaje mínimo no puede ser mayor al máximo")
        
        return await self.repository.find_by_commission_range(
            min_commission, max_commission
        )
