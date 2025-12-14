from typing import Optional
from app.domain.washers.repositories.washer_repository import IWasherRepository
from app.core.security import verify_password, create_access_token
from app.application.dto.auth.token_response import TokenResponse

class LoginWasher:
    def __init__(self, repo: IWasherRepository):
        self.repo = repo

    async def execute(self, email: str, password: str) -> Optional[TokenResponse]:
        washer = await self.repo.get_by_email(email)
        if not washer:
            return None
        
        if not washer.password_hash:
            return None

        if not verify_password(password, washer.password_hash):
            return None
            
        if not washer.is_active:
            return None 
            
        if washer.id:
            # Washer entity doesn't have last_login currently
            pass
            
        access_token = create_access_token(subject=washer.id, additional_claims={"role": "washer"})
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=washer.id,
            email=washer.email,
            role="washer"
        )
