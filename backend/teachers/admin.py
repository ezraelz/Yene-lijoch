from django.contrib import admin

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'get_teacher_name',
        'church',
        'employment_date',
    )

    list_filter = (
        'church',
        'employment_date',
    )

    search_fields = (
        'profile__first_name',
        'profile__last_name',
        'profile__email',
        'church__name',
    )

    ordering = (
        'id',
    )

    @admin.display(description='Teacher Name')
    def get_teacher_name(self, obj):
        return (
            f"{obj.profile.first_name} "
            f"{obj.profile.last_name}"
        )