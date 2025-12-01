from datetime import date, timedelta
from typing import List
from app.domain.notifications.entities.notification import Notification
from app.domain.notifications.repositories.notification_repository import INotificationRepository
from app.domain.subscriptions.repositories.subscription_repository import ISubscriptionRepository

class CheckExpiringSubscriptionsUseCase:
    """Use case to check for subscriptions expiring soon and create notifications"""
    
    def __init__(
        self,
        notification_repo: INotificationRepository,
        subscription_repo: ISubscriptionRepository
    ):
        self.notification_repo = notification_repo
        self.subscription_repo = subscription_repo
    
    async def execute(self, days_threshold: int = 7, admin_id: int = 1) -> List[Notification]:
        """
        Check for subscriptions expiring within threshold days and create notifications.
        
        Args:
            days_threshold: Number of days to look ahead for expiring subscriptions
            admin_id: ID of the admin to notify
            
        Returns:
            List of created notifications
        """
        today = date.today()
        expiring_subscriptions = await self.subscription_repo.list_expiring(today, days_threshold)
        
        notifications = []
        
        for subscription in expiring_subscriptions:
            days_remaining = (subscription.end_date - today).days
            
            # Create notification
            notification = Notification(
                id=None,
                recipient_type="operational_admin",
                recipient_id=admin_id,
                notification_type="info" if days_remaining > 3 else "warning",
                title="Suscripción Próxima a Vencer",
                message=f"La suscripción del vehículo ID {subscription.vehicle_id} vence en {days_remaining} días. "
                        f"Fecha de vencimiento: {subscription.end_date.strftime('%d/%m/%Y')}",
                is_read=False
            )
            
            created = await self.notification_repo.create(notification)
            notifications.append(created)
        
        return notifications
