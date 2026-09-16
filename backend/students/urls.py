from django.urls import path
from .views import (
    StudentSearchView,
    StudentListCreateAPIView,
    StudentDetailAPIView,
    StudentRegisterAPIView,
)

urlpatterns = [
    path("students/search/", StudentSearchView.as_view(), name="student-search"),
    path("students/", StudentListCreateAPIView.as_view(), name="student-list-create"),
    path("students/<int:pk>/", StudentDetailAPIView.as_view(), name="student-detail"),
    path("students/register/", StudentRegisterAPIView.as_view(), name="student-register"),
]