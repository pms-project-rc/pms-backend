from datetime import datetime
from app.domain.financial.entities.shift import Shift
from app.domain.financial.repositories.shift_repository import ShiftRepository

class StartShift:
    def __init__(self, shift_repository: ShiftRepository):
        self.shift_repository = shift_repository

    async def execute(self, admin_id: int, initial_cash: int) -> Shift:
        # Check if there is an active shift
        active_shift = await self.shift_repository.get_active_shift_by_admin(admin_id)
        if active_shift:
            raise ValueError("El administrador ya tiene un turno activo.")

        new_shift = Shift(
            admin_id=admin_id,
            shift_date=datetime.now().date(),
            start_time=datetime.now(),
            initial_cash=initial_cash,
            total_income=0,
            total_expenses=0
        )

        return await self.shift_repository.save(new_shift)
