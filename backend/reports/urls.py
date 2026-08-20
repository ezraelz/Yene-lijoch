from django.urls import path
from .views import (
    ReportsDashboardAPIView,
    StudentReportAPIView,
    TeacherReportAPIView,
    ParentReportAPIView,
    AttendanceReportAPIView,
    StudentAttendanceReportAPIView,
    AttendanceReportDownloadAPIView,
)


urlpatterns = [
    path(
        "dashboard/",
        ReportsDashboardAPIView.as_view(),
        name="reports-dashboard"
    ),
    path(
        "students/",
        StudentReportAPIView.as_view(),
        name="student-report"
    ),
    path(
        "teachers/",
        TeacherReportAPIView.as_view(),
        name="teacher-report"
    ),
    path(
        "parents/",
        ParentReportAPIView.as_view(),
        name="parent-report"
    ),
    path(
        "attendance/",
        AttendanceReportAPIView.as_view(),
        name="attendance-report"
    ),
    path(
        "attendance/students/",
        StudentAttendanceReportAPIView.as_view(),
        name="student-attendance-report"
    ),
    path(
        "attendance/download/",
        AttendanceReportDownloadAPIView.as_view(),
        name="student-attendance-download"
    ),
]