from django.urls import path

from .views import (
    ParentListCreateAPIView,
    ParentDetailAPIView,
)


urlpatterns = [
    path(
        "parents/",
        ParentListCreateAPIView.as_view(),
        name="parent-list-create",
    ),

    path(
        "parents/<int:pk>/",
        ParentDetailAPIView.as_view(),
        name="parent-detail",
    ),
]