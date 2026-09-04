from django.contrib import admin

from .models import ClassRoom


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "organization__name",
        "teacher",
        "room",
        "status",
        "start_date",
        "end_date",
        "get_students_count",
    )

    list_filter = (
        "organization__name",
        "status",
        "start_date",
    )

    search_fields = (
        "name",
        "description",
        "room",
        "organization__name",
        "teacher__profile__first_name",
        "teacher__profile__last_name",
        "students__profile__first_name",
        "students__profile__last_name",
    )

    filter_horizontal = (
        "students",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    @admin.display(description="Students")
    def get_students_count(self, obj):
        return obj.students.count()

    fieldsets = (
        (
            "Class Information",
            {
                "fields": (
                    "organization",
                    "name",
                    "description",
                    "teacher",
                )
            }
        ),

        (
            "Students",
            {
                "fields": (
                    "students",
                )
            }
        ),

        (
            "Schedule",
            {
                "fields": (
                    "start_date",
                    "end_date",
                    "room",
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
