from datetime import datetime, timezone, timedelta
from typing import List
from app.domain.notifications.entities.notification import Notification
from app.domain.notifications.repositories.notification_repository import INotificationRepository
from app.domain.parking.repositories.parking_record_repository import IParkingRecordRepository

class CheckLongParkingVehiclesUseCase:
    """Use case to check for vehicles parked for too long and create notifications"""
    
    def __init__(
        self,
        notification_repo: INotificationRepository,
        parking_record_repo: IParkingRecordRepository
    ):
        self.notification_repo = notification_repo
        self.parking_record_repo = parking_record_repo
    
    async def execute(self, hours_threshold: int = 12, admin_id: int = 1) -> List[Notification]:
        """
        Check for vehicles parked longer than threshold and create notifications.
        
        Args:
            hours_threshold: Number of hours to consider as "too long"
            admin_id: ID of the admin to notify
            
        Returns:
            List of created notifications
        """
        # Get all active parking records
        active_records = await self.parking_record_repo.list_active()
        
        notifications = []
        current_time = datetime.now(timezone.utc)
        threshold_time = timedelta(hours=hours_threshold)
        
        for record in active_records:
            duration = current_time - record.entry_time
            
            if duration > threshold_time:
                hours_parked = int(duration.total_seconds() / 3600)
                
                # Create notification
                notification = Notification(
                    id=None,
                    recipient_type="operational_admin",
                    recipient_id=admin_id,
                    notification_type="warning",
                    title="Vehículo con Mucho Tiempo Estacionado",
                    message=f"El vehículo ID {record.vehicle_id} lleva {hours_parked} horas estacionado. "
                            f"Entrada: {record.entry_time.strftime('%d/%m/%Y %H:%M')}",
                    is_read=False
                )
                
                created = await self.notification_repo.create(notification)
                notifications.append(created)
        
        return notifications
