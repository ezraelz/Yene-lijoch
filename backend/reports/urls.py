from django.urls import path

from .views import (
    DashboardReportAPIView,
    StudentReportAPIView,
    TeacherReportAPIView,
    ParentReportAPIView,
    AttendanceReportAPIView,
    StudentAttendanceReportAPIView,
)


urlpatterns = [

    path(
        "dashboard/",
        DashboardReportAPIView.as_view(),
        name="dashboard-report"
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
]