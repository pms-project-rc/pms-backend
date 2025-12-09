from fastapi import APIRouter, HTTPException, Depends, status
from app.application.dto.auth.login_request import LoginRequest
from app.application.dto.auth.token_response import TokenResponse
from app.application.dto.auth.password_reset_request import PasswordResetRequest
from app.application.dto.auth.password_reset_confirm import PasswordResetConfirm
from app.domain.users.use_cases.login_global_admin import LoginGlobalAdmin
from app.domain.users.use_cases.login_operational_admin import LoginOperationalAdmin
from app.domain.users.use_cases.request_password_reset import RequestPasswordReset
from app.domain.users.use_cases.reset_password import ResetPassword
from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl
from app.infrastructure.repositories.users.operational_admin_repository_impl import OperationalAdminRepositoryImpl
from app.infrastructure.repositories.washers.washer_repository_impl import WasherRepositoryImpl
from app.core.security import verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_global_admin_repo():
    return GlobalAdminRepositoryImpl()

def get_operational_admin_repo():
    return OperationalAdminRepositoryImpl()

def get_washer_repo():
    return WasherRepositoryImpl()

@router.post("/login", response_model=TokenResponse)
async def login_unified(
    data: LoginRequest, 
    global_repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo),
    operational_repo: OperationalAdminRepositoryImpl = Depends(get_operational_admin_repo),
    washer_repo: WasherRepositoryImpl = Depends(get_washer_repo)
):
    """
    Unified login endpoint that tries to authenticate with any role:
    1. Global Admin
    2. Operational Admin
    3. Washer
    """
    
    # Try Global Admin
    uc = LoginGlobalAdmin(global_repo)
    token = await uc.execute(data.email, data.password)
    if token:
        return token
    
    # Try Operational Admin
    uc = LoginOperationalAdmin(operational_repo)
    token = await uc.execute(data.email, data.password)
    if token:
        return token
    
    # Try Washer
    washer = await washer_repo.get_by_email(data.email)
    if washer:
        if verify_password(data.password, washer.password_hash):
            if washer.is_active and washer.id:
                access_token = create_access_token(
                    subject=washer.id, 
                    additional_claims={
                        "role": "washer",
                        "user_id": washer.id,
                        "username": washer.email
                    }
                )
                return TokenResponse(
                    access_token=access_token,
                    token_type="bearer",
                    user_id=washer.id,
                    email=washer.email,
                    role="washer"
                )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

@router.post("/login/global-admin", response_model=TokenResponse)
async def login_global_admin(
    data: LoginRequest, 
    repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo)
):
    uc = LoginGlobalAdmin(repo)
    token = await uc.execute(data.email, data.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/login/operational-admin", response_model=TokenResponse)
async def login_operational_admin(
    data: LoginRequest, 
    repo: OperationalAdminRepositoryImpl = Depends(get_operational_admin_repo)
):
    uc = LoginOperationalAdmin(repo)
    token = await uc.execute(data.email, data.password)
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token

@router.post("/forgot-password")
async def request_password_reset(
    data: PasswordResetRequest,
    repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo)
):
    uc = RequestPasswordReset(repo)
    await uc.execute(data.email)
    return {"message": "If the email exists, a reset link has been sent."}

@router.post("/reset-password")
async def reset_password(
    data: PasswordResetConfirm,
    repo: GlobalAdminRepositoryImpl = Depends(get_global_admin_repo)
):
    uc = ResetPassword(repo)
    success = await uc.execute(data.token, data.new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    return {"message": "Password updated successfully"}
