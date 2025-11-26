from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token
from app.domain.users.entities.user import User
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.users.sqlalchemy_user_repository import SqlAlchemyUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        session: Database session
        
    Returns:
        User: Authenticated user
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user_repository = SqlAlchemyUserRepository(session)
    user = await user_repository.get_by_username(username)
    
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency to ensure the current user is active.
    
    Args:
        current_user: User from get_current_user dependency
        
    Returns:
        User: Active user
        
    Raises:
        HTTPException: 400 if user is inactive
    """
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
