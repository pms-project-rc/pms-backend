from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.session import get_session
from app.infrastructure.repositories.users.user_repository_impl import UserRepositoryImpl

from app.domain.users.use_cases.create_user import CreateUser
from app.domain.users.use_cases.list_users import ListUsers
from app.domain.users.use_cases.get_user import GetUser
from app.domain.users.use_cases.update_user import UpdateUser
from app.domain.users.use_cases.delete_user import DeleteUser

from app.application.dto.users.user_request import UserCreateRequest, UserUpdateRequest
from app.application.dto.users.user_response import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


# CREATE
@router.post("/", response_model=UserResponse)
async def create_user(data: UserCreateRequest, session: AsyncSession = Depends(get_session)):
    repo = UserRepositoryImpl(session)
    use_case = CreateUser(repo)
    user = await use_case.execute(data)
    return UserResponse.from_entity(user)


# LIST ALL
@router.get("/", response_model=list[UserResponse])
async def list_users(session: AsyncSession = Depends(get_session)):
    repo = UserRepositoryImpl(session)
    use_case = ListUsers(repo)
    users = await use_case.execute()
    return [UserResponse.from_entity(u) for u in users]


# GET ONE
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, session: AsyncSession = Depends(get_session)):
    repo = UserRepositoryImpl(session)
    use_case = GetUser(repo)
    user = await use_case.execute(user_id)
    return UserResponse.from_entity(user)


# UPDATE
@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, data: UserUpdateRequest, session: AsyncSession = Depends(get_session)):
    repo = UserRepositoryImpl(session)
    use_case = UpdateUser(repo)
    user = await use_case.execute(user_id, data)
    return UserResponse.from_entity(user)


# DELETE
@router.delete("/{user_id}")
async def delete_user(user_id: int, session: AsyncSession = Depends(get_session)):
    repo = UserRepositoryImpl(session)
    use_case = DeleteUser(repo)
    await use_case.execute(user_id)
    return {"message": "User deleted successfully"}
