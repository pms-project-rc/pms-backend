from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.schemas.expense_schemas import ExpenseCreate, ExpenseResponse
from app.application.financial.services.register_expense import RegisterExpense
from app.application.financial.services.delete_expense import DeleteExpense
from app.application.financial.services.list_expenses import ListExpenses
from app.infrastructure.repositories.financial.expense_repository_impl import ExpenseRepositoryImpl
from app.api.dependencies.auth import get_current_user

router = APIRouter(prefix="/expenses", tags=["Expenses"])

def get_repository():
    return ExpenseRepositoryImpl()

@router.post("/", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense: ExpenseCreate,
    repository: ExpenseRepositoryImpl = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    use_case = RegisterExpense(repository)
    return await use_case.execute(
        expense_type=expense.expense_type,
        amount=expense.amount,
        description=expense.description,
        expense_date=expense.expense_date,
        shift_id=expense.shift_id
    )

@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    skip: int = 0,
    limit: int = 100,
    repository: ExpenseRepositoryImpl = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    use_case = ListExpenses(repository)
    return await use_case.execute(skip=skip, limit=limit)

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    expense_id: int,
    repository: ExpenseRepositoryImpl = Depends(get_repository),
    current_user = Depends(get_current_user)
):
    use_case = DeleteExpense(repository)
    await use_case.execute(expense_id)
