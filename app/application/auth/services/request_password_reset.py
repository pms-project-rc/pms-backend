from app.domain.users.repositories.global_admin_repository import IGlobalAdminRepository
from app.core.security import create_password_reset_token

class RequestPasswordReset:
    def __init__(self, repo: IGlobalAdminRepository):
        self.repo = repo

    async def execute(self, email: str) -> bool:
        admin = await self.repo.get_by_email(email)
        if not admin:
            # Return True to avoid enumerating users
            return True
        
        token = create_password_reset_token(email)
        
        # TODO: Integrate with real Email Service
        # For now, we just print it to stdout/logs so we can test it
        print(f"============================================")
        print(f"PASSWORD RESET TOKEN FOR {email}:")
        print(f"{token}")
        print(f"============================================")
        
        return True
