from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.users.login_user import LoginUser, LoginUserDTO, TokenDTO
from app.domain.users.exceptions.user_exceptions import InvalidCredentialsException, UserNotFoundException
from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.users.sqlalchemy_user_repository import SqlAlchemyUserRepository

router = APIRouter()

async def get_user_repository(session: AsyncSession = Depends(get_session)) -> SqlAlchemyUserRepository:
    return SqlAlchemyUserRepository(session)

@router.post("/login", response_model=TokenDTO)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repository: SqlAlchemyUserRepository = Depends(get_user_repository)
):
    use_case = LoginUser(user_repository)
    dto = LoginUserDTO(username=form_data.username, password=form_data.password)
    
    try:
        return await use_case.execute(dto)
    except (InvalidCredentialsException, UserNotFoundException) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
