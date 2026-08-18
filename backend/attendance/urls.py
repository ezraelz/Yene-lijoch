from django.urls import path

from .views import (
    AttendanceListCreateAPIView,
    AttendanceDetailAPIView,
)


urlpatterns = [

    path(
        "attendance/",
        AttendanceListCreateAPIView.as_view(),
        name="attendance-list-create",
    ),

    path(
        "attendance/<int:pk>/",
        AttendanceDetailAPIView.as_view(),
        name="attendance-detail",
    ),

]