from django.urls import path
from .views import (
    LessonListCreateAPIView,
    LessonDetailAPIView,
    LessonMakeThisWeekAPIView,
    LessonTogglePublishAPIView,
    LessonSetDateAPIView,
    LessonTodayAPIView,
    LessonUpcomingAPIView,
)

urlpatterns = [
    path("lessons/", LessonListCreateAPIView.as_view(), name="lesson-list-create"),
    path("lessons/today/", LessonTodayAPIView.as_view(), name="lesson-today"),
    path("lessons/upcoming/", LessonUpcomingAPIView.as_view(), name="lesson-upcoming"),
    path("lessons/<int:pk>/", LessonDetailAPIView.as_view(), name="lesson-detail"),
    path("lessons/<int:pk>/make-this-week/", LessonMakeThisWeekAPIView.as_view(), name="lesson-make-this-week"),
    path("lessons/<int:pk>/toggle-publish/", LessonTogglePublishAPIView.as_view(), name="lesson-toggle-publish"),
    path("lessons/<int:pk>/set-date/", LessonSetDateAPIView.as_view(), name="lesson-set-date"), 
]