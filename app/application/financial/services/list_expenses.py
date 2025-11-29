from typing import List
from app.domain.financial.entities.expense import Expense
from app.domain.financial.repositories.expense_repository import ExpenseRepository

class ListExpenses:
    def __init__(self, expense_repository: ExpenseRepository):
        self.expense_repository = expense_repository

    async def execute(self, skip: int = 0, limit: int = 100) -> List[Expense]:
        return await self.expense_repository.get_all(skip, limit)
