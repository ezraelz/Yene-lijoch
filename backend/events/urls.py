from django.urls import path
from .views import (
    EventListCreateAPIView,
    EventDetailAPIView,
    EventTogglePublishAPIView,
)

urlpatterns = [
    path("events/", EventListCreateAPIView.as_view(), name="event-list-create"),
    path("events/<int:pk>/", EventDetailAPIView.as_view(), name="event-detail"),
    path("events/<int:pk>/toggle-publish/", EventTogglePublishAPIView.as_view(), name="event-toggle-publish"),
]