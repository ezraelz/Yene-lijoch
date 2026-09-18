# notifications/api/urls.py
from django.urls import include
from django.urls import path
from rest_framework.routers import DefaultRouter
from notifications.views import (
    NotificationViewSet,
    NotificationUnreadAPIView,
    NotificationMarkReadAPIView,
    NotificationMarkAllReadAPIView,
)

router = DefaultRouter()

router.register(
    "",
    NotificationViewSet,
    basename="notifications",
)

urlpatterns = [
    # Explicit APIView routes MUST come before the router include,
    # otherwise the router's detail route (`<pk>/`) can swallow them.
    path(
        "notifications/unread/",
        NotificationUnreadAPIView.as_view(),
        name="notifications-unread",
    ),
    path(
        "notifications/mark-all-read/",
        NotificationMarkAllReadAPIView.as_view(),
        name="notifications-mark-all-read",
    ),
    path(
        "notifications/<int:pk>/mark-read/",
        NotificationMarkReadAPIView.as_view(),
        name="notifications-mark-read",
    ),
    path(
        "notifications/",
        include(router.urls),
    ),
]