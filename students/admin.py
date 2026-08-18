from django.contrib import admin

from .models import Student


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "get_student_name",
        "get_username",
        "church",
        "guardian_name",
        "guardian_contact",
        "status",
        "enrollment_date",
    )

    list_filter = (
        "status",
        "church",
        "enrollment_date",
    )

    search_fields = (
        "profile__username",
        "profile__first_name",
        "profile__last_name",
        "profile__email",
        "guardian_name",
        "guardian_contact",
    )

    ordering = (
        "id",
    )

    @admin.display(description="Student Name")
    def get_student_name(self, obj):
        return (
            f"{obj.profile.first_name} "
            f"{obj.profile.last_name}"
        )

    @admin.display(description="Username")
    def get_username(self, obj):
        return obj.profile.username
    