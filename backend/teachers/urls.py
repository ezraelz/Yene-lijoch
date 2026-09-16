from django.urls import path
from .views import (
    TeacherMeAPIView,
    TeacherListCreateAPIView,
    TeacherDetailAPIView,
)

urlpatterns = [
    path("teachers/me/", TeacherMeAPIView.as_view(), name="teacher-me"),
    path("teachers/", TeacherListCreateAPIView.as_view(), name="teacher-list-create"),
    path("teachers/<int:pk>/", TeacherDetailAPIView.as_view(), name="teacher-detail"),
]
