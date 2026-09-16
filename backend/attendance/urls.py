from django.urls import path
from .views import (
    AttendanceListCreateAPIView,
    AttendanceBulkCreateAPIView,
    AttendanceSummaryAPIView,
    AttendanceDetailAPIView,
)

urlpatterns = [
    path("attendance/", AttendanceListCreateAPIView.as_view(), name="attendance-list-create"),
    path("attendance/bulk/", AttendanceBulkCreateAPIView.as_view(), name="attendance-bulk"),
    path("attendance/summary/", AttendanceSummaryAPIView.as_view(), name="attendance-summary"),
    path("attendance/<int:pk>/", AttendanceDetailAPIView.as_view(), name="attendance-detail"),
]
