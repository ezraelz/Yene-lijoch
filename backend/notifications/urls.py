from django.urls import path

from .views import (
    MarkAllNotificationsReadView,
    MarkNotificationReadView,
    NotificationListView,
    RegisterPushTokenView,
    UnreadCountView,
)

app_name = "notifications"

urlpatterns = [
    path("notifications/push-token/", RegisterPushTokenView.as_view(), name="push-token"),
    path("notifications/", NotificationListView.as_view(), name="list"),
    path("notifications/unread-count/", UnreadCountView.as_view(), name="unread-count"),
    path("notifications/mark-all-read/", MarkAllNotificationsReadView.as_view(), name="mark-all-read"),
    path("notifications/<int:pk>/mark-read/", MarkNotificationReadView.as_view(), name="mark-read"),
]
