from typing import List, Optional
from datetime import date
from sqlalchemy import select, update, delete, func, cast, Date, and_
from app.domain.washers.entities.washer import Washer
from app.domain.washers.repositories.washer_repository import IWasherRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.users import Washer as WasherModel
from app.infrastructure.database.models.services import WashingService as WashingServiceModel
from app.infrastructure.database.models.financial import EmployeeAdvance as AdvanceModel


class WasherRepositoryImpl(IWasherRepository):
    def _to_entity(self, model: WasherModel) -> Optional[Washer]:
        if not model:
            return None
        return Washer(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            phone=model.phone,
            commission_percentage=model.commission_percentage,
            is_active=model.is_active,
            password_hash=model.password_hash
        )

    def _to_model(self, entity: Washer) -> WasherModel:
        return WasherModel(
            id=entity.id,
            full_name=entity.full_name,
            email=entity.email,
            phone=entity.phone,
            commission_percentage=entity.commission_percentage,
            is_active=entity.is_active,
            password_hash=entity.password_hash
        )

    async def create(self, washer: Washer) -> Washer:
        async with SessionLocal() as session:
            model = self._to_model(washer)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def list(self) -> List[Washer]:
        async with SessionLocal() as session:
            result = await session.execute(select(WasherModel))
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def get(self, washer_id: int) -> Optional[Washer]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(WasherModel).where(WasherModel.id == washer_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def update(self, washer_id: int, washer: Washer) -> Washer:
        async with SessionLocal() as session:
            stmt = (
                update(WasherModel)
                .where(WasherModel.id == washer_id)
                .values(
                    full_name=washer.full_name,
                    email=washer.email,
                    phone=washer.phone,
                    commission_percentage=washer.commission_percentage,
                    is_active=washer.is_active,
                    password_hash=washer.password_hash
                )
            )
            await session.execute(stmt)
            await session.commit()

            result = await session.execute(
                select(WasherModel).where(WasherModel.id == washer_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def delete(self, washer_id: int) -> bool:
        print(f"DEBUG: WasherRepository deleting id {washer_id}")
        async with SessionLocal() as session:
            result = await session.execute(
                select(WasherModel).where(WasherModel.id == washer_id)
            )
            model = result.scalar_one_or_none()
            if model:
                print(f"DEBUG: Washer found: {model.email}, deleting...")
                try:
                    await session.delete(model)
                    await session.commit()
                    print("DEBUG: Delete committed")
                    return True
                except Exception as e:
                    print(f"DEBUG: Error during delete commit: {e}")
                    raise e
            print("DEBUG: Washer not found")
            return False

    async def update_all_commission(self, percentage: int):
        async with SessionLocal() as session:
            stmt = (
                update(WasherModel)
                .values(commission_percentage=percentage)
            )
            await session.execute(stmt)
            await session.commit()

    async def count_active(self) -> int:
        async with SessionLocal() as session:
            result = await session.execute(
                select(func.count(WasherModel.id)).where(WasherModel.is_active == True)
            )
            return result.scalar() or 0

    async def get_by_email(self, email: str) -> Optional[Washer]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(WasherModel).where(WasherModel.email == email)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    # Alias for consistency with other repositories
    async def get_by_id(self, washer_id: int) -> Optional[Washer]:
        return await self.get(washer_id)

    async def get_payroll_summary(self, start_date: date, end_date: date) -> List[dict]:
        async with SessionLocal() as session:
            # 1. Get all washers
            washers_result = await session.execute(select(WasherModel))
            washers = washers_result.scalars().all()
            
            summary = []
            
            for washer in washers:
                # Calculate total commission from washing services
                # Commission = price * (washer.commission_percentage / 100)
                # Note: We use the washer's CURRENT commission percentage. 
                # Ideally, historical commission should be stored in WashingService, but for now we use current.
                # Wait, if we want accuracy, we should check if WashingService stores commission.
                # Looking at WashingService model, it has 'price' but not 'commission'.
                # So we must calculate it.
                
                commission_query = select(
                    func.sum(WashingServiceModel.price)
                ).where(
                    WashingServiceModel.washer_id == washer.id,
                    cast(WashingServiceModel.service_date, Date) >= start_date,
                    cast(WashingServiceModel.service_date, Date) <= end_date,
                    WashingServiceModel.payment_status == 'paid' # Only paid services count? Usually yes.
                )
                
                commission_result = await session.execute(commission_query)
                total_sales = commission_result.scalar() or 0
                total_bonus = int(total_sales * (washer.commission_percentage / 100))
                
                # Calculate total advances
                advances_query = select(
                    func.sum(AdvanceModel.total_amount)
                ).where(
                    AdvanceModel.washer_id == washer.id,
                    cast(AdvanceModel.created_at, Date) >= start_date,
                    cast(AdvanceModel.created_at, Date) <= end_date,
                    AdvanceModel.status != 'cancelled'
                )
                
                advances_result = await session.execute(advances_query)
                total_advances = advances_result.scalar() or 0
                
                summary.append({
                    "washer_id": washer.id,
                    "washer_name": washer.full_name,
                    "total_bonus": total_bonus,
                    "total_advances": total_advances,
                    "total_to_pay": total_bonus - total_advances
                })
                
            return summary

    async def get_washer_payroll_detail(self, washer_id: int, start_date: date, end_date: date) -> List[dict]:
        async with SessionLocal() as session:
            # Get washer to know commission percentage
            washer_result = await session.execute(select(WasherModel).where(WasherModel.id == washer_id))
            washer = washer_result.scalar_one_or_none()
            
            if not washer:
                return []
                
            # Get daily sales
            sales_query = select(
                cast(WashingServiceModel.service_date, Date).label('date'),
                func.sum(WashingServiceModel.price).label('total_sales')
            ).where(
                WashingServiceModel.washer_id == washer_id,
                cast(WashingServiceModel.service_date, Date) >= start_date,
                cast(WashingServiceModel.service_date, Date) <= end_date,
                WashingServiceModel.payment_status == 'paid'
            ).group_by(
                cast(WashingServiceModel.service_date, Date)
            )
            
            sales_result = await session.execute(sales_query)
            sales_by_date = {row.date: row.total_sales for row in sales_result}
            
            # Get daily advances
            advances_query = select(
                cast(AdvanceModel.created_at, Date).label('date'),
                func.sum(AdvanceModel.total_amount).label('total_advances')
            ).where(
                AdvanceModel.washer_id == washer_id,
                cast(AdvanceModel.created_at, Date) >= start_date,
                cast(AdvanceModel.created_at, Date) <= end_date,
                AdvanceModel.status != 'cancelled'
            ).group_by(
                cast(AdvanceModel.created_at, Date)
            )
            
            advances_result = await session.execute(advances_query)
            advances_by_date = {row.date: row.total_advances for row in advances_result}
            
            # Merge dates
            all_dates = sorted(list(set(sales_by_date.keys()) | set(advances_by_date.keys())))
            
            detail = []
            for d in all_dates:
                daily_sales = sales_by_date.get(d, 0)
                daily_bonus = int(daily_sales * (washer.commission_percentage / 100))
                daily_advances = advances_by_date.get(d, 0)
                
                detail.append({
                    "date": d,
                    "total_washed": daily_sales,
                    "total_bonus": daily_bonus,
                    "total_advances": daily_advances,
                    "total_to_pay": daily_bonus - daily_advances
                })
                
            return detail
        """Alias for get() method to maintain consistency with other repositories"""
        return await self.get(washer_id)
