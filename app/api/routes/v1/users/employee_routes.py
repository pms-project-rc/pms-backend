from typing import List
from fastapi import APIRouter, Depends, HTTPException
from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl
from app.infrastructure.repositories.users.operational_admin_repository_impl import OperationalAdminRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.domain.users.use_cases.list_all_employees import ListAllEmployees
from app.domain.users.use_cases.create_employee import CreateEmployee
from app.domain.users.use_cases.delete_employee import DeleteEmployee
from app.domain.users.use_cases.update_employee import UpdateEmployee
from app.application.dto.users.employee_response import EmployeeResponse
from app.application.dto.users.employee_create_request import EmployeeCreateRequest
from app.application.dto.users.employee_update_request import EmployeeUpdateRequest

router = APIRouter(prefix="/users/employees", tags=["Employees"])


def get_global_admin_repo():
    return GlobalAdminRepositoryImpl()


def get_operational_admin_repo():
    return OperationalAdminRepositoryImpl()


def get_washer_repo():
    return WasherRepositoryImpl()


@router.get("/", response_model=List[EmployeeResponse])
async def list_all_employees(
    global_admin_repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo),
    operational_admin_repo: OperationalAdminRepositoryImpl = Depends(get_operational_admin_repo),
    washer_repo: WasherRepositoryImpl = Depends(get_washer_repo)
):
    """
    Lista todos los empleados del sistema (Global Admins, Operational Admins y Washers).
    """
    uc = ListAllEmployees(global_admin_repo, operational_admin_repo, washer_repo)
    return await uc.execute()


@router.post("/", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    data: EmployeeCreateRequest,
    global_admin_repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo),
    operational_admin_repo: OperationalAdminRepositoryImpl = Depends(get_operational_admin_repo),
    washer_repo: WasherRepositoryImpl = Depends(get_washer_repo)
):
    """
    Crea un nuevo empleado en el sistema.
    """
    uc = CreateEmployee(global_admin_repo, operational_admin_repo, washer_repo)
    return await uc.execute(data)


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: int,
    role: str,  # 'global_admin', 'operational_admin', 'washer'
    global_admin_repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo),
    operational_admin_repo: OperationalAdminRepositoryImpl = Depends(get_operational_admin_repo),
    washer_repo: WasherRepositoryImpl = Depends(get_washer_repo)
):
    """
    Elimina un empleado del sistema.
    
    Query params:
    - role: Rol del empleado a eliminar ('global_admin', 'operational_admin', 'washer')
    """

    print(f"DEBUG: Request to delete employee {employee_id} with role {role}")
    uc = DeleteEmployee(global_admin_repo, operational_admin_repo, washer_repo)
    try:
        await uc.execute(employee_id, role)
        print(f"DEBUG: Successfully deleted employee {employee_id}")
        return {"deleted": True, "message": "Employee deleted successfully"}
    except Exception as e:
        print(f"DEBUG: Error deleting employee: {str(e)}")
        raise e


@router.put("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: int,
    role: str,  # 'global_admin', 'operational_admin', 'washer'
    data: EmployeeUpdateRequest,
    global_admin_repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo),
    operational_admin_repo: OperationalAdminRepositoryImpl = Depends(get_operational_admin_repo),
    washer_repo: WasherRepositoryImpl = Depends(get_washer_repo)
):
    """
    Actualiza un empleado del sistema.
    
    Query params:
    - role: Rol del empleado a actualizar ('global_admin', 'operational_admin', 'washer')
    """
    uc = UpdateEmployee(global_admin_repo, operational_admin_repo, washer_repo)
    return await uc.execute(employee_id, role, data)
