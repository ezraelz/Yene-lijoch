from django.urls import path

from .views import (
    ParentListCreateAPIView,
    ParentDetailAPIView,
    ParentMeView,
    AdminParentView
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

    path(
        "parents/me/",
        ParentMeView.as_view(),
        name="parent-me",
    ),

    path(
        "admin-parents/",
        AdminParentView.as_view(),
        name="parent-admin",
    ),
]