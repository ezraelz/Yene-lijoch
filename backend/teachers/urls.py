from django.urls import path

from .views import (
    TeacherListCreateAPIView,
    TeacherDetailAPIView,
)


urlpatterns = [
    path(
        'teachers/',
        TeacherListCreateAPIView.as_view(),
        name='teacher-list-create'
    ),

    path(
        'teachers/<int:pk>/',
        TeacherDetailAPIView.as_view(),
        name='teacher-detail'
    ),
]