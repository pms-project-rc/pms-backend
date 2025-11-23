"""
Interfaces de repositorios para el módulo de usuarios (Ports).

Estas interfaces definen los contratos que deben implementar
los adapters de infraestructura.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.users.entities import GlobalAdmin, OperationalAdmin, Washer


class UserRepositoryInterface(ABC):
    """
    Interfaz base para repositorios de usuarios.
    
    Define las operaciones comunes para todos los tipos de usuarios.
    """
    
    @abstractmethod
    async def save(self, user) -> None:
        """
        Guarda o actualiza un usuario en el repositorio.
        
        Args:
            user: Entidad de usuario (GlobalAdmin, OperationalAdmin o Washer)
        """
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: int):
        """
        Busca un usuario por su ID.
        
        Args:
            user_id: ID del usuario
            
        Returns:
            Entidad de usuario si existe, None si no
        """
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str):
        """
        Busca un usuario por su email.
        
        Args:
            email: Email del usuario
            
        Returns:
            Entidad de usuario si existe, None si no
        """
        pass
    
    @abstractmethod
    async def delete(self, user_id: int) -> bool:
        """
        Elimina un usuario del repositorio.
        
        Args:
            user_id: ID del usuario a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100):
        """
        Obtiene todos los usuarios con paginación.
        
        Args:
            skip: Número de registros a saltar
            limit: Número máximo de registros a retornar
            
        Returns:
            Lista de entidades de usuario
        """
        pass


class GlobalAdminRepository(UserRepositoryInterface):
    """Interfaz de repositorio para Global Admins."""
    
    @abstractmethod
    async def save(self, admin: GlobalAdmin) -> GlobalAdmin:
        """Guarda o actualiza un Global Admin."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[GlobalAdmin]:
        """Busca un Global Admin por ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[GlobalAdmin]:
        """Busca un Global Admin por email."""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[GlobalAdmin]:
        """Obtiene todos los Global Admins."""
        pass
    
    @abstractmethod
    async def find_active(self) -> List[GlobalAdmin]:
        """Obtiene todos los Global Admins activos."""
        pass


class OperationalAdminRepository(UserRepositoryInterface):
    """Interfaz de repositorio para Operational Admins."""
    
    @abstractmethod
    async def save(self, admin: OperationalAdmin) -> OperationalAdmin:
        """Guarda o actualiza un Operational Admin."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[OperationalAdmin]:
        """Busca un Operational Admin por ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[OperationalAdmin]:
        """Busca un Operational Admin por email."""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[OperationalAdmin]:
        """Obtiene todos los Operational Admins."""
        pass
    
    @abstractmethod
    async def find_active(self) -> List[OperationalAdmin]:
        """Obtiene todos los Operational Admins activos."""
        pass


class WasherRepository(UserRepositoryInterface):
    """Interfaz de repositorio para Washers."""
    
    @abstractmethod
    async def save(self, washer: Washer) -> Washer:
        """Guarda o actualiza un Washer."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[Washer]:
        """Busca un Washer por ID."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[Washer]:
        """Busca un Washer por email."""
        pass
    
    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> List[Washer]:
        """Obtiene todos los Washers."""
        pass
    
    @abstractmethod
    async def find_active(self) -> List[Washer]:
        """Obtiene todos los Washers activos."""
        pass
    
    @abstractmethod
    async def find_by_commission_range(
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
        pass
