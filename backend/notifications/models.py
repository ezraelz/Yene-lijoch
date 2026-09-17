from django.conf import settings
from django.db import models


class PushToken(models.Model):
    """
    An Expo push token registered by a device for a given user.

    A user can have multiple tokens (multiple devices logged in at once).
    A token is unique across the whole table because the same physical
    device/install can only ever hand out one live token at a time -- if
    it gets re-registered under a different user (e.g. logout/login as a
    different account on a shared device), we want the old row moved over
    rather than duplicated.
    """

    PLATFORM_IOS = "ios"
    PLATFORM_ANDROID = "android"
    PLATFORM_WEB = "web"
    PLATFORM_CHOICES = [
        (PLATFORM_IOS, "iOS"),
        (PLATFORM_ANDROID, "Android"),
        (PLATFORM_WEB, "Web"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="push_tokens",
    )
    token = models.CharField(max_length=255, unique=True, db_index=True)
    platform = models.CharField(max_length=10, choices=PLATFORM_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=["user"])]

    def __str__(self):
        return f"{self.user_id} ({self.platform}) - {self.token[:16]}..."


class Notification(models.Model):
    """
    A single in-app/push notification delivered to one user.

    `notification_type` is a free-form short code ("new_message",
    "conversation_created", ...) so the frontend can decide how to
    render/route each notification without us needing a new model or
    migration for every new event type. `data` carries whatever payload
    the frontend needs for deep-linking (e.g. {"conversation_id": 12}).
    """

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        help_text="The user who triggered this notification, if any.",
    )
    notification_type = models.CharField(max_length=50, db_index=True)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    data = models.JSONField(default=dict, blank=True)
    read = models.BooleanField(default=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "read"]),
            models.Index(fields=["recipient", "created_at"]),
        ]

    def __str__(self):
        return f"[{self.notification_type}] -> {self.recipient_id}: {self.title}"
