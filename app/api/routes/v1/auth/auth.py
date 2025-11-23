from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_db
from app.api.schemas.auth import Token, LoginRequest
from app.application.auth.login_use_case import LoginUseCase
from app.infrastructure.repositories import (
    SQLAlchemyGlobalAdminRepository,
    SQLAlchemyOperationalAdminRepository,
    SQLAlchemyWasherRepository,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    print(f"DEBUG: Login attempt for {request.email}")
    print(f"DEBUG: Password received: '{request.password}' (len: {len(request.password)})")
    
    # Initialize repositories
    global_repo = SQLAlchemyGlobalAdminRepository(db)
    operational_repo = SQLAlchemyOperationalAdminRepository(db)
    washer_repo = SQLAlchemyWasherRepository(db)
    
    # Initialize use case
    use_case = LoginUseCase(global_repo, operational_repo, washer_repo)
    
    try:
        token = await use_case.execute(request.email, request.password)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Email o contraseña incorrectos",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token
    except ValueError as e:
        # Handle inactive user case
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
