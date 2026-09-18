import logging

from django.contrib.auth import get_user_model

from ..models import Notification, PushToken

logger = logging.getLogger(__name__)

User = get_user_model()


def notify_user(
    recipient,
    notification_type: str,
    title: str,
    body: str = "",
    data: dict | None = None,
    actor=None,
    push: bool = True,
):
    """
    Create a Notification row for `recipient` and, unless `push=False`,
    fan it out as an Expo push notification to all of their registered
    devices. Safe to call from request-response code (small, synchronous)
    or from a background task/signal handler.

    `data` should be a small, JSON-serializable dict used for client-side
    deep-linking (e.g. {"conversation_id": 12, "screen": "chat"}).
    """
    data = data or {}

    notification = Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        title=title,
        body=body,
        data=data,
    )

    if push:
        send_push_to_user(recipient, title, body, data)

    return notification


def send_push_to_user(user, title: str, body: str, data: dict | None = None):
    """
    Send an Expo push notification to every device registered for `user`.
    Silently no-ops if the user has no registered tokens, and prunes any
    tokens Expo reports as dead so we stop wasting sends on them.
    """
    tokens = list(PushToken.objects.filter(user=user).values_list("token", flat=True))
    if not tokens:
        return

    try:
        # Imported lazily so the package is only required in environments
        # that actually send push notifications (e.g. not in every test run).
        from exponent_server_sdk import (
            DeviceNotRegisteredError,
            PushClient,
            PushMessage,
            PushServerError,
            PushTicketError,
        )
    except ImportError:
        logger.warning(
            "exponent_server_sdk is not installed; skipping push send. "
            "Install it with `pip install exponent-server-sdk`."
        )
        return

    client = PushClient()
    messages = [
        PushMessage(to=token, title=title, body=body, data=data or {})
        for token in tokens
    ]

    dead_tokens = []
    try:
        tickets = client.publish_multiple(messages)
    except PushServerError as exc:
        logger.error("Expo push server error: %s", exc)
        return
    except Exception:
        logger.exception("Unexpected error sending Expo push notifications")
        return

    for token, ticket in zip(tokens, tickets):
        try:
            ticket.validate_response()
        except DeviceNotRegisteredError:
            dead_tokens.append(token)
        except PushTicketError as exc:
            logger.warning("Push ticket error for token %s: %s", token, exc)

    if dead_tokens:
        PushToken.objects.filter(token__in=dead_tokens).delete()


def notify_users(recipients, notification_type: str, title: str, body: str = "", data: dict | None = None, actor=None, push: bool = True):
    """Convenience wrapper for fanning the same notification out to several users."""
    return [
        notify_user(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            body=body,
            data=data,
            actor=actor,
            push=push,
        )
        for recipient in recipients
    ]
