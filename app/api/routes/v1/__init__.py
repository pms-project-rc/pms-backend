from fastapi import APIRouter
from app.api.routes.v1.users import router as users_router


router = APIRouter()

# Aquí registramos las rutas de usuarios
router.include_router(users_router, prefix="/users", tags=["Users"])

