from fastapi import APIRouter, HTTPException, Depends, status
from app.application.dto.auth.login_request import LoginRequest
from app.application.dto.auth.token_response import TokenResponse
from app.application.dto.auth.password_reset_request import PasswordResetRequest
from app.application.dto.auth.password_reset_confirm import PasswordResetConfirm
from app.application.auth.services.login_global_admin import LoginGlobalAdmin
from app.application.auth.services.request_password_reset import RequestPasswordReset
from app.application.auth.services.reset_password import ResetPassword
from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl

router = APIRouter(prefix="/auth", tags=["Authentication"])

def get_global_admin_repo():
    return GlobalAdminRepositoryImpl()

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
