from typing import Optional
from datetime import datetime
from sqlalchemy import select, and_
from app.domain.financial.entities.shift import Shift
from app.domain.financial.repositories.shift_repository import ShiftRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.financial import Shift as ShiftModel

class ShiftRepositoryImpl(ShiftRepository):

    def _to_entity(self, model: ShiftModel) -> Optional[Shift]:
        if not model:
            return None
        return Shift(
            id=model.id,
            admin_id=model.admin_id,
            washer_id=model.washer_id,
            shift_date=model.shift_date,
            start_time=model.start_time,
            end_time=model.end_time,
            initial_cash=model.initial_cash,
            final_cash=model.final_cash,
            total_income=model.total_income,
            total_expenses=model.total_expenses,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    async def save(self, shift: Shift) -> Shift:
        async with SessionLocal() as session:
            if shift.id:
                # Update existing
                result = await session.execute(
                    select(ShiftModel).where(ShiftModel.id == shift.id)
                )
                model = result.scalar_one_or_none()
                if model:
                    model.end_time = shift.end_time
                    model.final_cash = shift.final_cash
                    model.total_income = shift.total_income
                    model.total_expenses = shift.total_expenses
                    model.notes = shift.notes
                    # We don't usually update start_time or initial_cash or admin_id
                    await session.commit()
                    await session.refresh(model)
                    return self._to_entity(model)
            
            # Create new
            model = ShiftModel(
                admin_id=shift.admin_id,
                washer_id=shift.washer_id,
                shift_date=shift.shift_date,
                start_time=shift.start_time,
                initial_cash=shift.initial_cash,
                total_income=shift.total_income,
                total_expenses=shift.total_expenses,
                notes=shift.notes
            )
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, shift_id: int) -> Optional[Shift]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ShiftModel).where(ShiftModel.id == shift_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def get_active_shift_by_admin(self, admin_id: int) -> Optional[Shift]:
        """Get active shift by admin_id or washer_id (method works for both)"""
        async with SessionLocal() as session:
            result = await session.execute(
                select(ShiftModel).where(
                    and_(
                        ShiftModel.end_time.is_(None),
                        (ShiftModel.admin_id == admin_id) | (ShiftModel.washer_id == admin_id)
                    )
                )
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def get_by_date_and_admin(self, date_val, admin_id: int) -> Optional[Shift]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(ShiftModel).where(
                    and_(
                        ShiftModel.admin_id == admin_id,
                        ShiftModel.shift_date == date_val
                    )
                )
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)
