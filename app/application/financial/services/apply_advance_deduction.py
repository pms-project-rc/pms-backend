from typing import List, Dict
from app.domain.financial.repositories.employee_advance_repository import EmployeeAdvanceRepository

class ApplyAdvanceDeduction:
    def __init__(self, repository: EmployeeAdvanceRepository):
        self.repository = repository

    async def execute(self, washer_id: int, max_deduction_amount: int) -> int:
        """
        Calcula el total a descontar hoy para un lavador y actualiza los saldos de los vales.
        Retorna el monto total descontado.
        """
        active_advances = await self.repository.get_active_by_washer(washer_id)
        total_deduction = 0
        remaining_capacity = max_deduction_amount

        for advance in active_advances:
            if remaining_capacity <= 0:
                break

            # Determine deduction amount for this period (e.g. daily/shift)
            # Logic: Deduct one installment amount, or the remaining if less.
            # Also limited by remaining_capacity (the bonus amount available)
            potential_deduction = min(advance.installment_amount, advance.remaining_amount)
            deduction = min(potential_deduction, remaining_capacity)
            
            if deduction > 0:
                advance.remaining_amount -= deduction
                if advance.remaining_amount <= 0:
                    advance.status = "paid"
                    advance.remaining_amount = 0
                
                await self.repository.save(advance)
                total_deduction += deduction
                remaining_capacity -= deduction

        return total_deduction

        return total_deduction
