from typing import List, Optional
from datetime import date
from sqlalchemy import select, update, and_, or_
from app.domain.subscriptions.entities.monthly_subscription import MonthlySubscription
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.subscriptions import MonthlySubscription as SubscriptionModel

class SubscriptionRepositoryImpl(ISubscriptionRepository):
    
    def _to_entity(self, model: SubscriptionModel) -> Optional[MonthlySubscription]:
        if not model:
            return None
        return MonthlySubscription(
            id=model.id,
            vehicle_id=model.vehicle_id,
            start_date=model.start_date,
            end_date=model.end_date,
            monthly_fee=model.monthly_fee,
            payment_status=model.payment_status,
            notes=model.notes,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def _to_model(self, entity: MonthlySubscription) -> SubscriptionModel:
        return SubscriptionModel(
            id=entity.id,
            vehicle_id=entity.vehicle_id,
            start_date=entity.start_date,
            end_date=entity.end_date,
            monthly_fee=entity.monthly_fee,
            payment_status=entity.payment_status,
            notes=entity.notes
        )

    async def create(self, subscription: MonthlySubscription) -> MonthlySubscription:
        async with SessionLocal() as session:
            model = self._to_model(subscription)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, subscription_id: int) -> Optional[MonthlySubscription]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(SubscriptionModel).where(SubscriptionModel.id == subscription_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def get_active_by_vehicle_id(self, vehicle_id: int, current_date: date) -> Optional[MonthlySubscription]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(SubscriptionModel)
                .where(SubscriptionModel.vehicle_id == vehicle_id)
                .where(SubscriptionModel.start_date <= current_date)
                .where(SubscriptionModel.end_date >= current_date)
                .where(SubscriptionModel.payment_status == 'paid')
                .order_by(SubscriptionModel.end_date.desc())
            )
            model = result.scalars().first()
            return self._to_entity(model)

    async def update(self, subscription_id: int, subscription: MonthlySubscription) -> MonthlySubscription:
        async with SessionLocal() as session:
            stmt = (
                update(SubscriptionModel)
                .where(SubscriptionModel.id == subscription_id)
                .values(
                    start_date=subscription.start_date,
                    end_date=subscription.end_date,
                    monthly_fee=subscription.monthly_fee,
                    payment_status=subscription.payment_status,
                    notes=subscription.notes
                )
            )
            await session.execute(stmt)
            await session.commit()
            
            result = await session.execute(
                select(SubscriptionModel).where(SubscriptionModel.id == subscription_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def list_active(self, current_date: date) -> List[MonthlySubscription]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(SubscriptionModel)
                .where(SubscriptionModel.start_date <= current_date)
                .where(SubscriptionModel.end_date >= current_date)
                .where(SubscriptionModel.payment_status == 'paid')
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def list_expiring(self, current_date: date, days_threshold: int) -> List[MonthlySubscription]:
        from datetime import timedelta
        target_date = current_date + timedelta(days=days_threshold)
        
        async with SessionLocal() as session:
            result = await session.execute(
                select(SubscriptionModel)
                .where(SubscriptionModel.end_date >= current_date)
                .where(SubscriptionModel.end_date <= target_date)
                .where(SubscriptionModel.payment_status == 'paid')
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def get_by_date_range(self, start_date: date, end_date: date) -> List[MonthlySubscription]:
        async with SessionLocal() as session:
            # We assume created_at reflects the payment date for new subscriptions
            # For renewals, if they update the record, we might miss them if we only check created_at.
            # However, usually renewals might create a new record or update updated_at.
            # Let's check created_at OR updated_at within range?
            # If updated_at is used, we might count non-financial updates.
            # Ideally we should have a Transaction table.
            # For now, let's use created_at as a proxy for "New Subscription Payment".
            # If the system updates existing records for renewal, we need to check updated_at too.
            # Given the previous context, let's stick to created_at for now, or cast to date.
            
            # Using cast to date for comparison
            from sqlalchemy import cast, Date
            
            result = await session.execute(
                select(SubscriptionModel)
                .where(cast(SubscriptionModel.created_at, Date) >= start_date)
                .where(cast(SubscriptionModel.created_at, Date) <= end_date)
                .where(SubscriptionModel.payment_status == 'paid')
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def list_all(self) -> List[MonthlySubscription]:
        """List all subscriptions (active and inactive)."""
        async with SessionLocal() as session:
            result = await session.execute(
                select(SubscriptionModel).order_by(SubscriptionModel.created_at.desc())
            )
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]
