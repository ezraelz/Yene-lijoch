from django.urls import path

from .views import (
    LessonListCreateAPIView,
    LessonDetailAPIView,
)


urlpatterns = [

    path(
        "lessons/",
        LessonListCreateAPIView.as_view(),
        name="lesson-list-create",
    ),

    path(
        "lessons/<int:pk>/",
        LessonDetailAPIView.as_view(),
        name="lesson-detail",
    ),

]