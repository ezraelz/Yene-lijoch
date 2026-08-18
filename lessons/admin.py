from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "classroom",
        "teacher",
        "lesson_date",
        "start_time",
        "end_time",
        "status",
    )

    list_filter = (
        "status",
        "lesson_date",
        "teacher",
        "classroom",
    )

    search_fields = (
        "title",
        "description",
        "content",
        "objectives",

        "classroom__name",

        "teacher__profile__first_name",
        "teacher__profile__last_name",
    )

    date_hierarchy = "lesson_date"

    ordering = (
        "-lesson_date",
        "-start_time",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (

        (
            "Lesson Information",
            {
                "fields": (
                    "classroom",
                    "teacher",
                    "title",
                    "description",
                )
            }
        ),

        (
            "Schedule",
            {
                "fields": (
                    "lesson_date",
                    "start_time",
                    "end_time",
                )
            }
        ),

        (
            "Lesson Content",
            {
                "fields": (
                    "content",
                    "objectives",
                )
            }
        ),

        (
            "Status",
            {
                "fields": (
                    "status",
                )
            }
        ),

        (
            "System Information",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            }
        ),
    )