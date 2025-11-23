"""
Endpoints REST para la gestión de usuarios.

Este módulo provee los endpoints de la API para crear, leer,
actualizar y eliminar usuarios de todos los tipos.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.api.dependencies import get_db
from app.api.schemas import (
    CreateGlobalAdminRequest,
    UpdateGlobalAdminRequest,
    GlobalAdminResponse,
    CreateOperationalAdminRequest,
    UpdateOperationalAdminRequest,
    OperationalAdminResponse,
    CreateWasherRequest,
    UpdateWasherRequest,
    WasherResponse,
    MessageResponse,
)
from app.application.users import (
    CreateGlobalAdminUseCase,
    GetGlobalAdminByIdUseCase,
    ListGlobalAdminsUseCase,
    UpdateGlobalAdminUseCase,
    DeleteGlobalAdminUseCase,
    CreateOperationalAdminUseCase,
    GetOperationalAdminByIdUseCase,
    ListOperationalAdminsUseCase,
    UpdateOperationalAdminUseCase,
    DeleteOperationalAdminUseCase,
    CreateWasherUseCase,
    GetWasherByIdUseCase,
    ListWashersUseCase,
    UpdateWasherUseCase,
    DeleteWasherUseCase,
    GetWashersByCommissionRangeUseCase,
)
from app.infrastructure.repositories import (
    SQLAlchemyGlobalAdminRepository,
    SQLAlchemyOperationalAdminRepository,
    SQLAlchemyWasherRepository,
)

# Importar bcrypt para hashear contraseñas
import bcrypt

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

router = APIRouter(prefix="/users", tags=["users"])


# ========== GLOBAL ADMINS ==========

@router.post(
    "/global-admins",
    response_model=GlobalAdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Global Admin",
    description="Crea un nuevo administrador global del sistema"
)
async def create_global_admin(
    request: CreateGlobalAdminRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo Global Admin."""
    # Hash de la contraseña
    password_hash = hash_password(request.password)
    
    # Crear repositorio y caso de uso
    repository = SQLAlchemyGlobalAdminRepository(db)
    use_case = CreateGlobalAdminUseCase(repository)
    
    try:
        admin = await use_case.execute(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            phone=request.phone
        )
        return admin
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/global-admins/{admin_id}",
    response_model=GlobalAdminResponse,
    summary="Obtener Global Admin por ID",
    description="Obtiene un administrador global por su ID"
)
async def get_global_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un Global Admin por ID."""
    repository = SQLAlchemyGlobalAdminRepository(db)
    use_case = GetGlobalAdminByIdUseCase(repository)
    
    admin = await use_case.execute(admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Global Admin con ID {admin_id} no encontrado"
        )
    return admin


@router.get(
    "/global-admins",
    response_model=List[GlobalAdminResponse],
    summary="Listar Global Admins",
    description="Lista todos los administradores globales con paginación"
)
async def list_global_admins(
    skip: int = 0,
    limit: int = 100,
    only_active: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Lista los Global Admins."""
    repository = SQLAlchemyGlobalAdminRepository(db)
    use_case = ListGlobalAdminsUseCase(repository)
    
    admins = await use_case.execute(skip=skip, limit=limit, only_active=only_active)
    return admins


@router.put(
    "/global-admins/{admin_id}",
    response_model=GlobalAdminResponse,
    summary="Actualizar Global Admin",
    description="Actualiza un administrador global existente"
)
async def update_global_admin(
    admin_id: int,
    request: UpdateGlobalAdminRequest,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza un Global Admin."""
    repository = SQLAlchemyGlobalAdminRepository(db)
    use_case = UpdateGlobalAdminUseCase(repository)
    
    admin = await use_case.execute(
        admin_id=admin_id,
        full_name=request.full_name,
        phone=request.phone,
        is_active=request.is_active
    )
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Global Admin con ID {admin_id} no encontrado"
        )
    return admin



@router.patch(
    "/global-admins/{admin_id}/toggle-active",
    response_model=GlobalAdminResponse,
    summary="Activar/Desactivar Global Admin",
    description="Cambia el estado activo/inactivo de un administrador global"
)
async def toggle_global_admin_active(
    admin_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Activa o desactiva un Global Admin."""
    repository = SQLAlchemyGlobalAdminRepository(db)
    
    # Obtener el admin actual
    get_use_case = GetGlobalAdminByIdUseCase(repository)
    admin = await get_use_case.execute(admin_id)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Global Admin con ID {admin_id} no encontrado"
        )
    
    # Cambiar el estado
    update_use_case = UpdateGlobalAdminUseCase(repository)
    updated_admin = await update_use_case.execute(
        admin_id=admin_id,
        full_name=admin.full_name,
        phone=admin.phone,
        is_active=not admin.is_active
    )
    
    return updated_admin


@router.delete(
    "/global-admins/{admin_id}",
    response_model=MessageResponse,
    summary="Eliminar Global Admin",
    description="Elimina un administrador global"
)
async def delete_global_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina un Global Admin."""
    repository = SQLAlchemyGlobalAdminRepository(db)
    use_case = DeleteGlobalAdminUseCase(repository)
    
    deleted = await use_case.execute(admin_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Global Admin con ID {admin_id} no encontrado"
        )
    
    return MessageResponse(message=f"Global Admin con ID {admin_id} eliminado exitosamente")



# ========== OPERATIONAL ADMINS ==========

@router.post(
    "/operational-admins",
    response_model=OperationalAdminResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Operational Admin"
)
async def create_operational_admin(
    request: CreateOperationalAdminRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo Operational Admin."""
    password_hash = hash_password(request.password)
    
    repository = SQLAlchemyOperationalAdminRepository(db)
    use_case = CreateOperationalAdminUseCase(repository)
    
    try:
        admin = await use_case.execute(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            phone=request.phone
        )
        return admin
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/operational-admins/{admin_id}",
    response_model=OperationalAdminResponse,
    summary="Obtener Operational Admin por ID"
)
async def get_operational_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un Operational Admin por ID."""
    repository = SQLAlchemyOperationalAdminRepository(db)
    use_case = GetOperationalAdminByIdUseCase(repository)
    
    admin = await use_case.execute(admin_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operational Admin con ID {admin_id} no encontrado"
        )
    return admin


@router.get(
    "/operational-admins",
    response_model=List[OperationalAdminResponse],
    summary="Listar Operational Admins"
)
async def list_operational_admins(
    skip: int = 0,
    limit: int = 100,
    only_active: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """Lista los Operational Admins."""
    repository = SQLAlchemyOperationalAdminRepository(db)
    use_case = ListOperationalAdminsUseCase(repository)
    
    admins = await use_case.execute(skip=skip, limit=limit, only_active=only_active)
    return admins


@router.put(
    "/operational-admins/{admin_id}",
    response_model=OperationalAdminResponse,
    summary="Actualizar Operational Admin"
)
async def update_operational_admin(
    admin_id: int,
    request: UpdateOperationalAdminRequest,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza un Operational Admin."""
    repository = SQLAlchemyOperationalAdminRepository(db)
    use_case = UpdateOperationalAdminUseCase(repository)
    
    admin = await use_case.execute(
        admin_id=admin_id,
        full_name=request.full_name,
        phone=request.phone,
        is_active=request.is_active
    )
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operational Admin con ID {admin_id} no encontrado"
        )
    return admin



@router.patch(
    "/operational-admins/{admin_id}/toggle-active",
    response_model=OperationalAdminResponse,
    summary="Activar/Desactivar Operational Admin"
)
async def toggle_operational_admin_active(
    admin_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Activa o desactiva un Operational Admin."""
    repository = SQLAlchemyOperationalAdminRepository(db)
    
    # Obtener el admin actual
    get_use_case = GetOperationalAdminByIdUseCase(repository)
    admin = await get_use_case.execute(admin_id)
    
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operational Admin con ID {admin_id} no encontrado"
        )
    
    # Cambiar el estado
    update_use_case = UpdateOperationalAdminUseCase(repository)
    updated_admin = await update_use_case.execute(
        admin_id=admin_id,
        full_name=admin.full_name,
        phone=admin.phone,
        is_active=not admin.is_active
    )
    
    return updated_admin


@router.delete(
    "/operational-admins/{admin_id}",
    response_model=MessageResponse,
    summary="Eliminar Operational Admin"
)
async def delete_operational_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina un Operational Admin."""
    repository = SQLAlchemyOperationalAdminRepository(db)
    use_case = DeleteOperationalAdminUseCase(repository)
    
    deleted = await use_case.execute(admin_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Operational Admin con ID {admin_id} no encontrado"
        )
    
    return MessageResponse(message=f"Operational Admin con ID {admin_id} eliminado exitosamente")



# ========== WASHERS ==========

@router.post(
    "/washers",
    response_model=WasherResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear Washer (Lavador)"
)
async def create_washer(
    request: CreateWasherRequest,
    db: AsyncSession = Depends(get_db)
):
    """Crea un nuevo Washer."""
    password_hash = hash_password(request.password)
    
    repository = SQLAlchemyWasherRepository(db)
    use_case = CreateWasherUseCase(repository)
    
    try:
        washer = await use_case.execute(
            email=request.email,
            password_hash=password_hash,
            full_name=request.full_name,
            phone=request.phone,
            commission_percentage=request.commission_percentage
        )
        return washer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/washers/{washer_id}",
    response_model=WasherResponse,
    summary="Obtener Washer por ID"
)
async def get_washer(
    washer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Obtiene un Washer por ID."""
    repository = SQLAlchemyWasherRepository(db)
    use_case = GetWasherByIdUseCase(repository)
    
    washer = await use_case.execute(washer_id)
    if not washer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Washer con ID {washer_id} no encontrado"
        )
    return washer


@router.get(
    "/washers",
    response_model=List[WasherResponse],
    summary="Listar Washers"
)
async def list_washers(
    skip: int = 0,
    limit: int = 100,
    only_active: bool = False,
    min_commission: int = None,
    max_commission: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Lista los Washers con filtros opcionales."""
    repository = SQLAlchemyWasherRepository(db)
    
    # Si se especifica rango de comisión, usar ese filtro
    if min_commission is not None and max_commission is not None:
        use_case = GetWashersByCommissionRangeUseCase(repository)
        try:
            washers = await use_case.execute(min_commission, max_commission)
            return washers
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # Caso normal: listado con paginación
    use_case = ListWashersUseCase(repository)
    washers = await use_case.execute(skip=skip, limit=limit, only_active=only_active)
    return washers


@router.put(
    "/washers/{washer_id}",
    response_model=WasherResponse,
    summary="Actualizar Washer"
)
async def update_washer(
    washer_id: int,
    request: UpdateWasherRequest,
    db: AsyncSession = Depends(get_db)
):
    """Actualiza un Washer."""
    repository = SQLAlchemyWasherRepository(db)
    use_case = UpdateWasherUseCase(repository)
    
    try:
        washer = await use_case.execute(
            washer_id=washer_id,
            full_name=request.full_name,
            phone=request.phone,
            commission_percentage=request.commission_percentage,
            is_active=request.is_active
        )
        
        if not washer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Washer con ID {washer_id} no encontrado"
            )
        return washer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )



@router.patch(
    "/washers/{washer_id}/toggle-active",
    response_model=WasherResponse,
    summary="Activar/Desactivar Washer"
)
async def toggle_washer_active(
    washer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Activa o desactiva un Washer."""
    repository = SQLAlchemyWasherRepository(db)
    
    # Obtener el washer actual
    get_use_case = GetWasherByIdUseCase(repository)
    washer = await get_use_case.execute(washer_id)
    
    if not washer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Washer con ID {washer_id} no encontrado"
        )
    
    # Cambiar el estado
    update_use_case = UpdateWasherUseCase(repository)
    try:
        updated_washer = await update_use_case.execute(
            washer_id=washer_id,
            full_name=washer.full_name,
            phone=washer.phone,
            commission_percentage=washer.commission_percentage,
            is_active=not washer.is_active
        )
        return updated_washer
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete(
    "/washers/{washer_id}",
    response_model=MessageResponse,
    summary="Eliminar Washer"
)
async def delete_washer(
    washer_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Elimina un Washer."""
    repository = SQLAlchemyWasherRepository(db)
    use_case = DeleteWasherUseCase(repository)
    
    deleted = await use_case.execute(washer_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Washer con ID {washer_id} no encontrado"
        )
    
    return MessageResponse(message=f"Washer con ID {washer_id} eliminado exitosamente")

