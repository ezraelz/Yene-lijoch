# notifications/services/notification_service.py
from django.db import transaction
from django.utils import timezone
from notifications.models import Notification
from notifications.services.websocket_service import WebSocketService
import logging
logger = logging.getLogger(__name__)

class NotificationService:
    @classmethod
    @transaction.atomic
    def create(cls,*,user,title,message,notification_type,data=None,
    ):
        """
        Create a notification and immediately broadcast it.
        """
        logger.info("NotificationService.create user=%s type=%s", user.id, notification_type)

        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            data=data or {},
        )

        transaction.on_commit(
            lambda: WebSocketService.send_notification(
                user.id,
                notification.to_payload(),
            )
        )
        def _send():
            logger.info(
                "on_commit fired: sending to user_%s for notif=%s",
                user.id, notification.id,
            )
            WebSocketService.send_notification(user.id, notification.to_payload())

        transaction.on_commit(_send)

        return notification

    @classmethod
    @transaction.atomic
    def broadcast(
        cls,
        *,
        users,
        title,
        message,
        notification_type,
        data=None,
    ):

        notifications = []

        for user in users:

            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
                data=data or {},
            )

            notifications.append(notification)

            transaction.on_commit(
                lambda user_id=user.id,
                       payload=notification.to_payload():
                    WebSocketService.send_notification(
                        user_id,
                        payload,
                    )
            )

        return notifications

    @staticmethod
    def mark_read(notification: Notification) -> Notification:
        """Mark a single notification as read. Idempotent."""
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()   # drop if you don't have this field
            notification.save(update_fields=["is_read", "read_at"])
        return notification

    @staticmethod
    def mark_all_read(user) -> int:
        """Mark every unread notification for `user` as read.
        Returns the number of rows updated."""
        return Notification.objects.filter(
            user=user,
            is_read=False,
        ).update(
            is_read=True,
            read_at=timezone.now(),   # drop if you don't have this field
        )
    