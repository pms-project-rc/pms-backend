from fastapi import APIRouter
from app.domain.users.use_cases.create_user import CreateUser
from app.domain.users.use_cases.list_users import ListUsers
from app.domain.users.use_cases.get_user import GetUser
from app.domain.users.use_cases.update_user import UpdateUser
from app.domain.users.use_cases.delete_user import DeleteUser

router = APIRouter()

@router.get("/")
async def list_all():
    return {"msg": "List users works"}

@router.post("/")
async def create():
    return {"msg": "Create works"}

@router.get("/{user_id}")
async def get_by_id(user_id: int):
    return {"msg": f"User {user_id}"}

@router.put("/{user_id}")
async def update(user_id: int):
    return {"msg": f"Update user {user_id}"}

@router.delete("/{user_id}")
async def delete(user_id: int):
    return {"msg": f"Delete user {user_id}"}
