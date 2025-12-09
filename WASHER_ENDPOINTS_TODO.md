# Endpoints Pendientes para Lavadores (Washers)

## Problema Actual
Los lavadores no pueden acceder a sus datos porque:
1. El endpoint `/washing/active` requiere `get_current_admin` (solo admins)
2. No existe una dependencia `get_current_washer` en `auth.py`
3. Los turnos (shifts) tampoco tienen endpoints específicos para lavadores

## Solución Requerida

### 1. Crear dependencia de autenticación para lavadores

**Archivo:** `app/api/dependencies/auth.py`

Agregar esta función:

```python
async def get_current_washer(token: str = Depends(oauth2_scheme)):
    """Get the current authenticated washer"""
    from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        
        if user_id is None:
            raise credentials_exception
            
        if user_role != "washer":
            raise credentials_exception
             
    except (JWTError, ValidationError):
        raise credentials_exception

    repo = WasherRepositoryImpl()
    
    try:
        user = await repo.get_by_id(int(user_id))
    except ValueError:
        raise credentials_exception
        
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive washer account"
        )
        
    return user
```

### 2. Crear endpoint para obtener servicios del lavador

**Archivo:** `app/api/routes/v1/washing/washing_routes.py`

Agregar este endpoint:

```python
@router.get("/my-services", response_model=List[WashingServiceResponse])
async def list_my_services(
    current_washer = Depends(get_current_washer)
):
    """
    List all washing services assigned to the current washer.
    Only returns services where washer_id matches current washer.
    """
    try:
        repo = WashingServiceRepositoryImpl()
        vehicle_repo = VehicleRepositoryImpl()
        
        # Obtener solo servicios asignados a este lavador
        services = await repo.list_by_washer(current_washer.id)
        
        response = []
        for s in services:
            vehicle = await vehicle_repo.get_by_id(s.vehicle_id)
            plate = vehicle.plate if vehicle else "UNKNOWN"

            response.append(WashingServiceResponse(
                id=s.id,
                vehicle_id=s.vehicle_id,
                plate=plate,
                service_type=s.service_type,
                price=s.price,
                status=s.payment_status,
                washer_id=s.washer_id,
                service_date=s.service_date
            ))
            
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing washer services: {str(e)}"
        )
```

### 3. Agregar método al repositorio de washing services

**Archivo:** `app/infrastructure/repositories/washing/washing_service_repository_impl.py`

Agregar este método:

```python
async def list_by_washer(self, washer_id: int) -> List[WashingServiceModel]:
    """Get all services assigned to a specific washer"""
    async with self.get_session() as session:
        query = select(WashingServiceORM).where(
            WashingServiceORM.washer_id == washer_id
        ).order_by(WashingServiceORM.service_date.desc())
        
        result = await session.execute(query)
        orms = result.scalars().all()
        return [self._to_model(orm) for orm in orms]
```

### 4. Actualizar endpoints de turnos (shifts) para lavadores

**Archivo:** `app/api/routes/v1/shifts/shift_routes.py` (si existe) o crear uno nuevo

Los endpoints de turnos deben aceptar tanto admins como lavadores:

```python
from app.api.dependencies.auth import get_current_admin, get_current_washer

# Crear una dependencia que acepte ambos
async def get_current_user_any(token: str = Depends(oauth2_scheme)):
    """Get current user (admin or washer)"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_role = payload.get("role")
        
        if user_role in ["global_admin", "operational_admin"]:
            return await get_current_admin(token)
        elif user_role == "washer":
            return await get_current_washer(token)
        else:
            raise HTTPException(status_code=401, detail="Invalid role")
    except:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

@router.get("/active")
async def get_active_shift(current_user = Depends(get_current_user_any)):
    # ... implementación
    
@router.post("/start")
async def start_shift(data: dict, current_user = Depends(get_current_user_any)):
    # ... implementación
    
@router.post("/close")
async def close_shift(current_user = Depends(get_current_user_any)):
    # ... implementación
```

## Pasos de Implementación

1. ✅ Agregar `get_current_washer()` a `auth.py`
2. ✅ Agregar `list_by_washer()` al repositorio de washing services
3. ✅ Crear endpoint `/washing/my-services`
4. ✅ Actualizar endpoints de shifts para aceptar lavadores
5. ✅ Probar con el usuario lavador (lavador@pms.com)

## Endpoints que debe tener un lavador

- `GET /api/v1/washing/my-services` - Ver sus servicios asignados
- `GET /api/v1/shifts/active` - Ver su turno activo
- `POST /api/v1/shifts/start` - Iniciar su turno
- `POST /api/v1/shifts/close` - Cerrar su turno
- `PUT /api/v1/washing/{service_id}/complete` - Marcar servicio como completado

## Frontend ya está listo

El frontend en `pms-frontend/src/services/washerDashboardService.ts` ya está configurado para usar estos endpoints. Una vez implementados en el backend, funcionará automáticamente.
