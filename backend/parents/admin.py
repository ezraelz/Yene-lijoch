from django.contrib import admin

from .models import Parent


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "get_parent_name",
        "get_username",
        "church",
        "relationship",
        "get_students",
    )

    list_filter = (
        "church",
        "relationship",
    )

    search_fields = (
        "profile__username",
        "profile__first_name",
        "profile__last_name",
        "profile__email",
        "profile__contact",
        "student__profile__first_name",
        "student__profile__last_name",
    )

    filter_horizontal = (
        "student",
    )

    ordering = (
        "id",
    )

    @admin.display(description="Parent Name")
    def get_parent_name(self, obj):
        return (
            f"{obj.profile.first_name} "
            f"{obj.profile.last_name}"
        )

    @admin.display(description="Username")
    def get_username(self, obj):
        return obj.profile.username

    @admin.display(description="Students")
    def get_students(self, obj):
        return ", ".join(
            f"{student.profile.first_name} "
            f"{student.profile.last_name}"
            for student in obj.student.all()
        )