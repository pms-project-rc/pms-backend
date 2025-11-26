from dataclasses import dataclass
from app.domain.users.repositories.user_repository import UserRepository
from app.domain.users.exceptions.user_exceptions import InvalidCredentialsException
from app.core.security import verify_password, create_access_token

@dataclass
class LoginUserDTO:
    username: str
    password: str

@dataclass
class TokenDTO:
    access_token: str
    token_type: str

class LoginUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def execute(self, data: LoginUserDTO) -> TokenDTO:
        user = await self.user_repository.get_by_username(data.username)
        
        print(f"DEBUG: Looking for user: {data.username}")
        print(f"DEBUG: User found: {user}")
        
        if not user:
            raise InvalidCredentialsException("Incorrect username or password")
            
        print(f"DEBUG: User password_hash: {user.password_hash}")
        print(f"DEBUG: Input password: {data.password}")
        
        if not verify_password(data.password, user.password_hash):
            print(f"DEBUG: Password verification failed")
            raise InvalidCredentialsException("Incorrect username or password")
            
        if not user.active:
             raise InvalidCredentialsException("User is inactive")

        access_token = create_access_token(data={
            "sub": user.username,
            "role": user.role,
            "user_id": user.id
        })
        return TokenDTO(access_token=access_token, token_type="bearer")
