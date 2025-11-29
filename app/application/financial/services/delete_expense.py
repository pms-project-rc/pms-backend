from app.domain.financial.repositories.expense_repository import ExpenseRepository

class DeleteExpense:
    def __init__(self, expense_repository: ExpenseRepository):
        self.expense_repository = expense_repository

    async def execute(self, expense_id: int) -> None:
        await self.expense_repository.delete(expense_id)
