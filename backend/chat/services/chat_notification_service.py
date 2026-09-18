import logging

from notifications.services.notification_service import NotificationService
logger = logging.getLogger(__name__)


class ChatNotificationType:
    """
    Wire values for Notification.notification_type. Centralized here so the frontend
    guide and any future notification-preferences UI can reference the same constants
    this service uses, instead of duplicating string literals.
    """

    NEW_VIDEO_ADDED = "new_video_added"
    NEW_MESSAGE = "new_chat_message"
    NEW_STUDENT = "new_student_added"
    NEW_LESSON = "new_lesson"
    NEW_PARENT_JOINED = "new_parent_joined"


class ChatNotificationService:

    @staticmethod
    def _safe_create(**kwargs):
        """Never let notification failures break the main business action."""
        try:
            NotificationService.create(**kwargs)
        except Exception:
            # In production: log the exception (Sentry, structlog, etc.)
            logger.exception("Failed to create chat notification")

    @classmethod
    def notify_new_message(cls, conversation, message, sender_role):
        logger.info(
            "notify_new_message called: conversation=%s message=%s sender_role=%r",
            conversation.id, message.id, sender_role,
        )

        if sender_role == "teacher":
            recipient = conversation.parent.profile
        else:
            recipient = conversation.teacher.profile

        logger.info(
            "resolved recipient: user_id=%s (parent_profile=%s teacher_profile=%s)",
            recipient.id,
            getattr(conversation.parent, "profile_id", None),
            getattr(conversation.teacher, "profile_id", None),
        )

        cls._safe_create(
            user=recipient,
            title="New message",
            message=message.text[:140],
            notification_type=ChatNotificationType.NEW_MESSAGE,
            data={"conversation_id": conversation.id, "screen": "chat"},
        )

        