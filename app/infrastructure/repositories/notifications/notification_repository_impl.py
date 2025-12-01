from typing import List, Optional
from datetime import datetime, timezone
from sqlalchemy import select, update, delete as sql_delete, func
from app.domain.notifications.entities.notification import Notification
from app.domain.notifications.repositories.notification_repository import INotificationRepository
from app.infrastructure.database.session import SessionLocal
from app.infrastructure.database.models.system import Notification as NotificationModel

class NotificationRepositoryImpl(INotificationRepository):
    
    def _to_entity(self, model: NotificationModel) -> Optional[Notification]:
        if not model:
            return None
        return Notification(
            id=model.id,
            recipient_type=model.recipient_type,
            recipient_id=model.recipient_id,
            notification_type=model.notification_type,
            title=model.title,
            message=model.message,
            is_read=model.is_read,
            read_at=model.read_at,
            created_at=model.created_at
        )

    def _to_model(self, entity: Notification) -> NotificationModel:
        return NotificationModel(
            id=entity.id,
            recipient_type=entity.recipient_type,
            recipient_id=entity.recipient_id,
            notification_type=entity.notification_type,
            title=entity.title,
            message=entity.message,
            is_read=entity.is_read,
            read_at=entity.read_at
        )

    async def create(self, notification: Notification) -> Notification:
        async with SessionLocal() as session:
            model = self._to_model(notification)
            session.add(model)
            await session.commit()
            await session.refresh(model)
            return self._to_entity(model)

    async def get_by_id(self, notification_id: int) -> Optional[Notification]:
        async with SessionLocal() as session:
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            model = result.scalar_one_or_none()
            return self._to_entity(model)

    async def mark_as_read(self, notification_id: int) -> Notification:
        async with SessionLocal() as session:
            stmt = (
                update(NotificationModel)
                .where(NotificationModel.id == notification_id)
                .values(is_read=True, read_at=datetime.now(timezone.utc))
            )
            await session.execute(stmt)
            await session.commit()
            
            result = await session.execute(
                select(NotificationModel).where(NotificationModel.id == notification_id)
            )
            model = result.scalar_one()
            return self._to_entity(model)

    async def list_by_recipient(
        self, 
        recipient_type: str, 
        recipient_id: int, 
        unread_only: bool = False
    ) -> List[Notification]:
        async with SessionLocal() as session:
            query = select(NotificationModel).where(
                NotificationModel.recipient_type == recipient_type,
                NotificationModel.recipient_id == recipient_id
            )
            
            if unread_only:
                query = query.where(NotificationModel.is_read == False)
            
            query = query.order_by(NotificationModel.created_at.desc())
            
            result = await session.execute(query)
            models = result.scalars().all()
            return [self._to_entity(m) for m in models]

    async def delete(self, notification_id: int):
        async with SessionLocal() as session:
            await session.execute(
                sql_delete(NotificationModel).where(NotificationModel.id == notification_id)
            )
            await session.commit()

    async def count_unread(self, recipient_type: str, recipient_id: int) -> int:
        async with SessionLocal() as session:
            result = await session.execute(
                select(func.count(NotificationModel.id))
                .where(NotificationModel.recipient_type == recipient_type)
                .where(NotificationModel.recipient_id == recipient_id)
                .where(NotificationModel.is_read == False)
            )
            return result.scalar() or 0
