from app.domain.financial.entities.employee_advance import EmployeeAdvance
from app.domain.financial.repositories.employee_advance_repository import EmployeeAdvanceRepository

class RegisterEmployeeAdvance:
    def __init__(self, repository: EmployeeAdvanceRepository):
        self.repository = repository

    async def execute(self, washer_id: int, amount: int, installments: int, description: str) -> EmployeeAdvance:
        if amount <= 0:
            raise ValueError("El monto debe ser mayor a 0")
        if installments <= 0:
            raise ValueError("El número de cuotas debe ser mayor a 0")

        installment_amount = amount // installments
        # Adjust last installment if needed? For simplicity, we assume integer division is fine for now, 
        # or we could store exact division. 
        # Let's keep it simple: installment_amount is floor, but we track remaining_amount.
        
        advance = EmployeeAdvance(
            washer_id=washer_id,
            total_amount=amount,
            number_of_installments=installments,
            installment_amount=installment_amount,
            remaining_amount=amount,
            description=description,
            status="active"
        )
        
        return await self.repository.save(advance)
