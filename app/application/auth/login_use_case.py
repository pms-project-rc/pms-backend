from typing import Optional, Tuple
from app.core.security import verify_password, create_access_token
from app.domain.users.repositories import (
    GlobalAdminRepository,
    OperationalAdminRepository,
)
from app.domain.washers import WasherRepository
from app.api.schemas.auth import Token


class LoginUseCase:
    """
    Use case for user login.
    Checks credentials against all user types repositories.
    """
    
    def __init__(
        self,
        global_admin_repo: GlobalAdminRepository,
        operational_admin_repo: OperationalAdminRepository,
        washer_repo: WasherRepository
    ):
        self.global_admin_repo = global_admin_repo
        self.operational_admin_repo = operational_admin_repo
        self.washer_repo = washer_repo

    async def execute(self, email: str, password: str) -> Optional[Token]:
        """
        Authenticate user and return token if valid.
        Returns None if authentication fails.
        """
        user = None
        role = None
        
        # 1. Check Global Admin
        user = await self.global_admin_repo.find_by_email(email)
        if user:
            role = "global_admin"
        
        # 2. Check Operational Admin
        if not user:
            user = await self.operational_admin_repo.find_by_email(email)
            if user:
                role = "operational_admin"
                
        # 3. Check Washer
        if not user:
            user = await self.washer_repo.find_by_email(email)
            if user:
                role = "washer"
        
        # If no user found or password invalid
        if not user or not verify_password(password, user.password_hash):
            return None
            
        # Check if user is active
        if not user.is_active:
            raise ValueError("Usuario inactivo. Contacte al administrador.")
            
        # Create Access Token
        access_token = create_access_token(
            subject=user.id,
            role=role
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            role=role,
            user_id=user.id,
            full_name=user.full_name
        )
