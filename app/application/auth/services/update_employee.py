from typing import Optional
from fastapi import HTTPException
from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl
from app.infrastructure.repositories.users.operational_admin_repository_impl import OperationalAdminRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.application.dto.users.employee_update_request import EmployeeUpdateRequest
from app.application.dto.users.employee_response import EmployeeResponse
from app.core.security import get_password_hash

class UpdateEmployee:
    """Caso de uso para actualizar un empleado existente."""
    
    def __init__(
        self,
        global_admin_repo: GlobalAdminRepositoryImpl,
        operational_admin_repo: OperationalAdminRepositoryImpl,
        washer_repo: WasherRepositoryImpl
    ):
        self.global_admin_repo = global_admin_repo
        self.operational_admin_repo = operational_admin_repo
        self.washer_repo = washer_repo
    
    async def execute(self, employee_id: int, role: str, data: EmployeeUpdateRequest) -> EmployeeResponse:
        """
        Ejecuta el caso de uso para actualizar un empleado.
        
        Args:
            employee_id: ID del empleado a actualizar.
            role: Rol del empleado.
            data: Datos a actualizar.
            
        Returns:
            EmployeeResponse: Empleado actualizado.
            
        Raises:
            HTTPException: Si el empleado no existe o el email ya está en uso.
        """
        
        # Validar que si se cambia el email, no exista ya
        if data.email:
            if await self._email_exists(data.email, employee_id, role):
                raise HTTPException(status_code=400, detail="Email already registered")

        if role == 'global_admin':
            return await self._update_global_admin(employee_id, data)
        elif role == 'operational_admin':
            return await self._update_operational_admin(employee_id, data)
        elif role == 'washer':
            return await self._update_washer(employee_id, data)
        else:
            raise HTTPException(status_code=400, detail="Invalid role")

    async def _update_global_admin(self, employee_id: int, data: EmployeeUpdateRequest) -> EmployeeResponse:
        admin = await self.global_admin_repo.get_by_id(employee_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Employee not found")
            
        if data.full_name is not None:
            admin.full_name = data.full_name
        if data.email is not None:
            admin.email = data.email
        if data.phone is not None:
            admin.phone = data.phone
        if data.is_active is not None:
            admin.is_active = data.is_active
        if data.password is not None:
            admin.password_hash = get_password_hash(data.password)
            
        updated_admin = await self.global_admin_repo.update(employee_id, admin)
        
        return EmployeeResponse(
            id=updated_admin.id,
            full_name=updated_admin.full_name,
            email=updated_admin.email,
            phone=updated_admin.phone,
            role='global_admin',
            is_active=updated_admin.is_active,
            created_at=updated_admin.created_at,
            commission_percentage=None
        )

    async def _update_operational_admin(self, employee_id: int, data: EmployeeUpdateRequest) -> EmployeeResponse:
        admin = await self.operational_admin_repo.get_by_id(employee_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Employee not found")
            
        if data.full_name is not None:
            admin.full_name = data.full_name
        if data.email is not None:
            admin.email = data.email
        if data.phone is not None:
            admin.phone = data.phone
        if data.is_active is not None:
            admin.is_active = data.is_active
        if data.password is not None:
            admin.password_hash = get_password_hash(data.password)
            
        updated_admin = await self.operational_admin_repo.update(employee_id, admin)
        
        return EmployeeResponse(
            id=updated_admin.id,
            full_name=updated_admin.full_name,
            email=updated_admin.email,
            phone=updated_admin.phone,
            role='operational_admin',
            is_active=updated_admin.is_active,
            created_at=updated_admin.created_at,
            commission_percentage=None
        )

    async def _update_washer(self, employee_id: int, data: EmployeeUpdateRequest) -> EmployeeResponse:
        washer = await self.washer_repo.get(employee_id)
        if not washer:
            raise HTTPException(status_code=404, detail="Employee not found")
            
        if data.full_name is not None:
            washer.full_name = data.full_name
        if data.email is not None:
            washer.email = data.email
        if data.phone is not None:
            washer.phone = data.phone
        if data.is_active is not None:
            washer.is_active = data.is_active
        if data.commission_percentage is not None:
            washer.commission_percentage = data.commission_percentage
        if data.password is not None:
            washer.password_hash = get_password_hash(data.password)
            
        updated_washer = await self.washer_repo.update(employee_id, washer)
        
        from datetime import datetime
        return EmployeeResponse(
            id=updated_washer.id,
            full_name=updated_washer.full_name,
            email=updated_washer.email,
            phone=updated_washer.phone,
            role='washer',
            is_active=updated_washer.is_active,
            created_at=datetime.now().isoformat(),  # Washer entity doesn't have created_at, using current time
            commission_percentage=updated_washer.commission_percentage
        )

    async def _email_exists(self, email: str, current_id: int, current_role: str) -> bool:
        """Verifica si un email ya existe en el sistema, excluyendo el usuario actual."""
        
        # Check global admin
        ga = await self.global_admin_repo.get_by_email(email)
        if ga and (current_role != 'global_admin' or ga.id != current_id):
            return True
            
        # Check operational admin
        oa = await self.operational_admin_repo.get_by_email(email)
        if oa and (current_role != 'operational_admin' or oa.id != current_id):
            return True
            
        # Check washer
        w = await self.washer_repo.get_by_email(email)
        if w and (current_role != 'washer' or w.id != current_id):
            return True
            
        return False
