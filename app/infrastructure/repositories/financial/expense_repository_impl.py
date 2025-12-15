from typing import List, Optional
from datetime import date
from sqlalchemy import select, delete, func
from app.domain.financial.entities.expense import Expense
from app.domain.financial.repositories.expense_repository import ExpenseRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.financial import Expense as ExpenseModel

class ExpenseRepositoryImpl(ExpenseRepository):

    def _to_entity(self, model: ExpenseModel) -> Optional[Expense]:
        if not model:
            return None
        return Expense(
            id=model.id,
            shift_id=model.shift_id,
            expense_type=model.expense_type,
            amount=model.amount,
            description=model.description,
            expense_date=model.expense_date,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def save(self, expense: Expense) -> Expense:
        async with SessionLocal() as session:
            # For now, we only handle creation as per HUs. 
            # If ID exists, we would update, but let's keep it simple for now.
            model = ExpenseModel(
                shift_id=expense.shift_id,
                expense_type=expense.expense_type,
                amount=expense.amount,
                description=expense.description,
                expense_date=expense.expense_date
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, expense_id: int) -> Optional[Expense]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ExpenseModel).where(ExpenseModel.id == expense_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def delete(self, expense_id: int) -> None:
        async with SessionLocal() as session:
            await session.execute(
                delete(ExpenseModel).where(ExpenseModel.id == expense_id)
            )
            await session.commit()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Expense]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ExpenseModel).offset(skip).limit(limit)
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def get_total_by_shift(self, shift_id: int) -> int:
        async with SessionLocal() as session:
            result = await session.execute(
                select(func.sum(ExpenseModel.amount))
                .where(ExpenseModel.shift_id == shift_id)
            )
            total = result.scalar()
            return total if total else 0

    async def get_sum_by_date_range(self, start_date: date, end_date: date) -> int:
        async with SessionLocal() as session:
            result = await session.execute(
                select(func.sum(ExpenseModel.amount))
                .where(ExpenseModel.expense_date >= start_date)
                .where(ExpenseModel.expense_date <= end_date)
            )
            total = result.scalar()
            return total if total else 0

    async def get_daily_expenses(self, start_date: date, end_date: date) -> List[dict]:
        async with SessionLocal() as session:
            stmt = (
                select(
                    ExpenseModel.expense_date,
                    func.sum(ExpenseModel.amount).label('total')
                )
                .where(ExpenseModel.expense_date >= start_date)
                .where(ExpenseModel.expense_date <= end_date)
                .group_by(ExpenseModel.expense_date)
                .order_by(ExpenseModel.expense_date)
            )
            result = await session.execute(stmt)
            return [{'date': row.expense_date, 'total': row.total} for row in result]

    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Expense]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ExpenseModel)
                .where(ExpenseModel.expense_date >= start_date)
                .where(ExpenseModel.expense_date <= end_date)
                .order_by(ExpenseModel.expense_date)
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]
