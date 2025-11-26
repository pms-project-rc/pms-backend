from app.domain.users.repositories.user_repository import IUsersRepository
from app.application.dto.users.user_request import UserUpdateRequest
from app.domain.users.entities.user import User

class UpdateUser:
    def __init__(self, repo: IUsersRepository):
        self.repo = repo

    async def execute(self, user_id: int, data: UserUpdateRequest):
        # Construimos la entidad con los datos proporcionados.
        # Ajusta si quieres que actualización sea parcial: aquí reemplazamos campos si vienen.
        existing = await self.repo.get(user_id)
        if not existing:
            return None

        updated = User(
            id=user_id,
            full_name=data.full_name if data.full_name is not None else existing.full_name,
            email=existing.email,  # no permitimos cambiar email aquí (cambiar si tu negocio lo requiere)
            phone=data.phone if data.phone is not None else existing.phone,
            status=data.status if data.status is not None else existing.status,
            created_at=existing.created_at
        )
        return await self.repo.update(user_id, updated)
