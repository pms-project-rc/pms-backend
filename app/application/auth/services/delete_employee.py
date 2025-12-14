from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl
from app.infrastructure.repositories.users.operational_admin_repository_impl import OperationalAdminRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from fastapi import HTTPException


class DeleteEmployee:
    """Caso de uso para eliminar un empleado."""
    
    def __init__(
        self,
        global_admin_repo: GlobalAdminRepositoryImpl,
        operational_admin_repo: OperationalAdminRepositoryImpl,
        washer_repo: WasherRepositoryImpl
    ):
        self.global_admin_repo = global_admin_repo
        self.operational_admin_repo = operational_admin_repo
        self.washer_repo = washer_repo
    
    async def execute(self, employee_id: int, role: str) -> bool:
        """
        Ejecuta el caso de uso para eliminar un empleado.
        
        Args:
            employee_id: ID del empleado.
            role: Rol del empleado ('global_admin', 'operational_admin', 'washer').
            
        Returns:
            bool: True si se eliminó correctamente.
            
        Raises:
            HTTPException: Si el rol es inválido o el empleado no existe.
        """
        if role == 'global_admin':
            result = await self.global_admin_repo.delete(employee_id)
        elif role == 'operational_admin':
            result = await self.operational_admin_repo.delete(employee_id)
        elif role == 'washer':
            result = await self.washer_repo.delete(employee_id)
        else:
            raise HTTPException(status_code=400, detail="Invalid role")
        
        if not result:
            raise HTTPException(status_code=404, detail="Employee not found")
        
        return True
