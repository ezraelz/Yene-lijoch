from django.urls import path
from .views import (
    ClassRoomListCreateAPIView,
    ClassRoomDetailAPIView,
    ClassRoomAddStudentAPIView,
    ClassRoomRemoveStudentAPIView,
    ClassRoomDeactivateAPIView,
)

urlpatterns = [
    path("classes/", ClassRoomListCreateAPIView.as_view(), name="class-list-create"),
    path("classes/<int:pk>/", ClassRoomDetailAPIView.as_view(), name="class-detail"),
    path("classes/<int:pk>/students/", ClassRoomAddStudentAPIView.as_view(), name="class-add-student"),
    path("classes/<int:pk>/students/<int:student_id>/", ClassRoomRemoveStudentAPIView.as_view(), name="class-remove-student"),
    path("classes/<int:pk>/deactivate/", ClassRoomDeactivateAPIView.as_view(), name="class-deactivate"),
]
