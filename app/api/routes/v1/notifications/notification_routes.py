from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from app.application.dto.notifications.notification_dtos import NotificationResponse
from app.infrastructure.repositories.notifications.notification_repository_impl import NotificationRepositoryImpl
from app.infrastructure.repositories.parking.parking_record_repository_impl import ParkingRecordRepositoryImpl
from app.infrastructure.repositories.subscriptions.subscription_repository_impl import SubscriptionRepositoryImpl
from app.application.notifications.check_long_parking_use_case import CheckLongParkingVehiclesUseCase
from app.application.notifications.check_expiring_subscriptions_use_case import CheckExpiringSubscriptionsUseCase
from app.api.dependencies.auth import get_current_operational_admin
from app.infrastructure.database.models.users import OperationalAdmin

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    List notifications for the current admin.
    """
    try:
        notification_repo = NotificationRepositoryImpl()
        notifications = await notification_repo.list_by_recipient(
            "operational_admin",
            current_admin.id,
            unread_only
        )
        
        return [
            NotificationResponse(
                id=n.id,
                recipient_type=n.recipient_type,
                recipient_id=n.recipient_id,
                notification_type=n.notification_type,
                title=n.title,
                message=n.message,
                is_read=n.is_read,
                read_at=n.read_at,
                created_at=n.created_at
            )
            for n in notifications
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing notifications: {str(e)}"
        )

@router.get("/unread/count")
async def count_unread_notifications(
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Count unread notifications for the current admin.
    """
    try:
        notification_repo = NotificationRepositoryImpl()
        count = await notification_repo.count_unread("operational_admin", current_admin.id)
        return {"unread_count": count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error counting notifications: {str(e)}"
        )

@router.put("/{notification_id}/read", response_model=NotificationResponse)
async def mark_notification_as_read(
    notification_id: int,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Mark a notification as read.
    """
    try:
        notification_repo = NotificationRepositoryImpl()
        
        # Verify notification belongs to current admin
        notification = await notification_repo.get_by_id(notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Notification {notification_id} not found"
            )
        
        if notification.recipient_id != current_admin.id or notification.recipient_type != "operational_admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this notification"
            )
        
        updated = await notification_repo.mark_as_read(notification_id)
        
        return NotificationResponse(
            id=updated.id,
            recipient_type=updated.recipient_type,
            recipient_id=updated.recipient_id,
            notification_type=updated.notification_type,
            title=updated.title,
            message=updated.message,
            is_read=updated.is_read,
            read_at=updated.read_at,
            created_at=updated.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error marking notification as read: {str(e)}"
        )

@router.post("/generate/long-parking")
async def generate_long_parking_notifications(
    hours_threshold: int = 12,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Manually trigger check for long-parked vehicles and generate notifications.
    """
    try:
        notification_repo = NotificationRepositoryImpl()
        parking_record_repo = ParkingRecordRepositoryImpl()
        
        use_case = CheckLongParkingVehiclesUseCase(notification_repo, parking_record_repo)
        notifications = await use_case.execute(hours_threshold, current_admin.id)
        
        return {
            "message": f"Generated {len(notifications)} notifications for long-parked vehicles",
            "count": len(notifications)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating notifications: {str(e)}"
        )

@router.post("/generate/expiring-subscriptions")
async def generate_expiring_subscriptions_notifications(
    days_threshold: int = 7,
    current_admin: OperationalAdmin = Depends(get_current_operational_admin)
):
    """
    Manually trigger check for expiring subscriptions and generate notifications.
    """
    try:
        notification_repo = NotificationRepositoryImpl()
        subscription_repo = SubscriptionRepositoryImpl()
        
        use_case = CheckExpiringSubscriptionsUseCase(notification_repo, subscription_repo)
        notifications = await use_case.execute(days_threshold, current_admin.id)
        
        return {
            "message": f"Generated {len(notifications)} notifications for expiring subscriptions",
            "count": len(notifications)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating notifications: {str(e)}"
        )
