from django.urls import path

from .views import (
    ClassRoomListCreateAPIView,
    ClassRoomDetailAPIView,
)


urlpatterns = [

    path(
        "classes/",
        ClassRoomListCreateAPIView.as_view(),
        name="class-list-create",
    ),

    path(
        "classes/<int:pk>/",
        ClassRoomDetailAPIView.as_view(),
        name="class-detail",
    ),

]