from datetime import date
from typing import Optional
from app.domain.financial.entities.expense import Expense
from app.domain.financial.repositories.expense_repository import ExpenseRepository

class RegisterExpense:
    def __init__(self, expense_repository: ExpenseRepository):
        self.expense_repository = expense_repository

    async def execute(self, expense_type: str, amount: int, description: str, expense_date: date, shift_id: Optional[int] = None) -> Expense:
        expense = Expense(
            expense_type=expense_type,
            amount=amount,
            description=description,
            expense_date=expense_date,
            shift_id=shift_id
        )
        return await self.expense_repository.save(expense)
