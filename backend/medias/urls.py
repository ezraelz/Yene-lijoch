from django.urls import path
from .views import (
    MediaItemListCreateAPIView,
    MediaItemDetailAPIView,
    MediaItemTogglePublishAPIView,
)

urlpatterns = [
    path("media/", MediaItemListCreateAPIView.as_view(), name="media-list-create"),
    path("media/<int:pk>/", MediaItemDetailAPIView.as_view(), name="media-detail"),
    path("media/<int:pk>/toggle-publish/", MediaItemTogglePublishAPIView.as_view(), name="media-toggle-publish"),
]