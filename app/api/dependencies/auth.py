from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core.config import settings
from app.core.security import ALGORITHM
from app.infrastructure.repositories.users.global_admin_repository_impl import GlobalAdminRepositoryImpl
from app.infrastructure.repositories.users.operational_admin_repository_impl import OperationalAdminRepositoryImpl

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/global-admin")
oauth2_scheme_operational = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login/operational-admin")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            print("User ID is None in payload")
            raise credentials_exception
    except (JWTError, ValidationError) as e:
        print(f"JWT Decode Error: {e}")
        raise credentials_exception
    
    # For now, we only have Global Admin repository. 
    # In the future, we might need to check other tables or a unified user table.
    repo = GlobalAdminRepositoryImpl()
    try:
        user_id_int = int(user_id)
        user = await repo.get_by_id(user_id_int)
    except ValueError:
        print(f"Invalid user ID format: {user_id}")
        raise credentials_exception

    if user is None:
        print(f"User not found for ID: {user_id}")
        raise credentials_exception
    return user


async def get_current_operational_admin(token: str = Depends(oauth2_scheme_operational)):
    """Get the current authenticated operational admin"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        user_role: str = payload.get("role")
        
        if user_id is None:
            print("User ID is None in payload")
            raise credentials_exception
            
        if user_role != "operational_admin":
            print(f"Invalid user role: {user_role}")
            raise credentials_exception
    except (JWTError, ValidationError) as e:
        print(f"JWT Decode Error: {e}")
        raise credentials_exception
    
    repo = OperationalAdminRepositoryImpl()
    try:
        user_id_int = int(user_id)
        user = await repo.get_by_id(user_id_int)
    except ValueError:
        print(f"Invalid user ID format: {user_id}")
        raise credentials_exception

    if user is None:
        print(f"Operational admin not found for ID: {user_id}")
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    
    return user

# Alias for clarity
get_current_global_admin = get_current_user
