from django.contrib import admin

from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "student_name",
        "lesson",
        "class_name",
        "status",
        "recorded_at",
    )

    list_filter = (
        "status",
        "lesson__lesson_date",
        "lesson__classroom",
    )

    search_fields = (
        "student__profile__first_name",
        "student__profile__last_name",
        "lesson__title",
        "lesson__classroom__name",
    )

    ordering = (
        "-lesson__lesson_date",
        "student__profile__first_name",
    )

    readonly_fields = (
        "recorded_at",
        "updated_at",
    )

    @admin.display(description="Student")
    def student_name(self, obj):

        return (
            f"{obj.student.profile.first_name} "
            f"{obj.student.profile.last_name}"
        )

    @admin.display(description="Class")
    def class_name(self, obj):

        return obj.lesson.classroom.name

    fieldsets = (

        (
            "Attendance Information",
            {
                "fields": (
                    "lesson",
                    "student",
                    "status",
                    "note",
                )
            }
        ),

        (
            "System Information",
            {
                "fields": (
                    "recorded_at",
                    "updated_at",
                )
            }
        ),
    )