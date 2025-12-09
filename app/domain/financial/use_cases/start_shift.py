from datetime import datetime
from app.domain.financial.entities.shift import Shift
from app.domain.financial.repositories.shift_repository import ShiftRepository

class StartShift:
    def __init__(self, shift_repository: ShiftRepository):
        self.shift_repository = shift_repository

    async def execute(self, admin_id: int = None, washer_id: int = None, initial_cash: int = 0) -> Shift:
        # Validar que al menos uno esté presente
        if not admin_id and not washer_id:
            raise ValueError("Se requiere admin_id o washer_id")
        
        # Check if there is an active shift for this user
        if admin_id:
            active_shift = await self.shift_repository.get_active_shift_by_admin(admin_id)
            user_type = "administrador"
            owner_id = admin_id
        else:
            # Para washers, usar una búsqueda similar
            active_shift = await self.shift_repository.get_active_shift_by_admin(washer_id)
            user_type = "lavador"
            owner_id = washer_id
        
        if active_shift:
            raise ValueError(f"El {user_type} ya tiene un turno activo.")

        new_shift = Shift(
            admin_id=admin_id,
            washer_id=washer_id,
            shift_date=datetime.now().date(),
            start_time=datetime.now(),
            initial_cash=initial_cash,
            total_income=0,
            total_expenses=0
        )

        return await self.shift_repository.save(new_shift)
