from typing import Optional
from app.domain.users.repositories.global_admin_repository import IGlobalAdminRepository
from app.core.security import verify_password_reset_token, get_password_hash

class ResetPassword:
    def __init__(self, repo: IGlobalAdminRepository):
        self.repo = repo

    async def execute(self, token: str, new_password: str) -> bool:
        email = verify_password_reset_token(token)
        if not email:
            return False
            
        admin = await self.repo.get_by_email(email)
        if not admin:
            return False
            
        new_hash = get_password_hash(new_password)
        await self.repo.update_password(admin.id, new_hash)
        return True
