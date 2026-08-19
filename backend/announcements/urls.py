from django.urls import path

from .views import (
    AnnouncementListCreateAPIView,
    AnnouncementDetailAPIView,
)


urlpatterns = [
    path(
        "",
        AnnouncementListCreateAPIView.as_view(),
        name="announcement-list-create"
    ),

    path(
        "<int:pk>/",
        AnnouncementDetailAPIView.as_view(),
        name="announcement-detail"
    ),
]