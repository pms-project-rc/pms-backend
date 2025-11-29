from typing import Optional
from app.domain.users.repositories.global_admin_repository import IGlobalAdminRepository
from app.core.security import verify_password, create_access_token
from app.application.dto.auth.token_response import TokenResponse

class LoginGlobalAdmin:
    def __init__(self, repo: IGlobalAdminRepository):
        self.repo = repo

    async def execute(self, email: str, password: str) -> Optional[TokenResponse]:
        admin = await self.repo.get_by_email(email)
        if not admin:
            return None
        
        if not verify_password(password, admin.password_hash):
            return None
            
        if not admin.is_active:
            return None 
            
        if admin.id:
            await self.repo.update_last_login(admin.id)
            
        access_token = create_access_token(subject=admin.id, additional_claims={"role": "global_admin"})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=admin.id,
            email=admin.email,
            role="global_admin"
        )
