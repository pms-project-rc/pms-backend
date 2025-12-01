from datetime import datetime
from app.domain.financial.entities.shift import Shift
from app.domain.financial.repositories.shift_repository import ShiftRepository
from app.domain.financial.repositories.expense_repository import ExpenseRepository
from app.domain.washing.repositories.washing_service_repository import IWashingServiceRepository
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository

class CloseShift:
    def __init__(
        self, 
        shift_repository: ShiftRepository,
        expense_repository: ExpenseRepository,
        washing_repository: IWashingServiceRepository,
        parking_repository: IParkingRecordRepository
    ):
        self.shift_repository = shift_repository
        self.expense_repository = expense_repository
        self.washing_repository = washing_repository
        self.parking_repository = parking_repository

    async def execute(self, admin_id: int) -> Shift:
        # Get active shift
        shift = await self.shift_repository.get_active_shift_by_admin(admin_id)
        if not shift:
            raise ValueError("No hay un turno activo para cerrar.")

        # Calculate totals
        washing_income = await self.washing_repository.get_total_income_by_shift(shift.id)
        parking_income = await self.parking_repository.get_total_income_by_shift(shift.id)
        total_expenses = await self.expense_repository.get_total_by_shift(shift.id)

        total_income = washing_income + parking_income
        
        # Update shift
        shift.end_time = datetime.now()
        shift.total_income = total_income
        shift.total_expenses = total_expenses
        shift.final_cash = shift.initial_cash + total_income - total_expenses
        
        # Save
        return await self.shift_repository.save(shift)
