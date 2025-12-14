from typing import List
from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl
from app.infrastructure.repositories.users.operational_admin_repository_impl import OperationalAdminRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.application.dto.users.employee_response import EmployeeResponse


class ListAllEmployees:
    """Caso de uso para listar todos los empleados del sistema."""
    
    def __init__(
        self,
        global_admin_repo: GlobalAdminRepositoryImpl,
        operational_admin_repo: OperationalAdminRepositoryImpl,
        washer_repo: WasherRepositoryImpl
    ):
        self.global_admin_repo = global_admin_repo
        self.operational_admin_repo = operational_admin_repo
        self.washer_repo = washer_repo
    
    async def execute(self) -> List[EmployeeResponse]:
        """
        Ejecuta el caso de uso para obtener todos los empleados.
        
        Returns:
            List[EmployeeResponse]: Lista unificada de todos los empleados.
        """
        employees = []
        
        # Obtener Global Admins - usando get_all que retorna modelos
        global_admins = await self.global_admin_repo.get_all()
        for admin in global_admins:
            employees.append(EmployeeResponse(
                id=admin.id,
                full_name=admin.full_name,
                email=admin.email,
                phone=admin.phone,
                role='global_admin',
                is_active=admin.is_active,
                created_at=admin.created_at,
                commission_percentage=None
            ))
        
        # Obtener Operational Admins - usando get_all que retorna modelos
        operational_admins = await self.operational_admin_repo.get_all()
        for admin in operational_admins:
            employees.append(EmployeeResponse(
                id=admin.id,
                full_name=admin.full_name,
                email=admin.email,
                phone=admin.phone,
                role='operational_admin',
                is_active=admin.is_active,
                created_at=admin.created_at,
                commission_percentage=None
            ))
        
        # Obtener Washers - accediendo directamente a la base de datos
        from app.infrastructure.database.models.users import Washer as WasherModel
        from app.infrastructure.database.session import SessionLocal
        from sqlalchemy import select
        
        async with SessionLocal() as session:
            result = await session.execute(select(WasherModel))
            washers = result.scalars().all()
            
            for washer in washers:
                employees.append(EmployeeResponse(
                    id=washer.id,
                    full_name=washer.full_name,
                    email=washer.email,
                    phone=washer.phone,
                    role='washer',
                    is_active=washer.is_active,
                    created_at=washer.created_at,
                    commission_percentage=washer.commission_percentage
                ))
        
        # Ordenar por fecha de creación descendente
        employees.sort(key=lambda x: x.created_at, reverse=True)
        
        return employees
