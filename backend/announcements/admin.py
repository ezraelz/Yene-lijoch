from django.contrib import admin

from .models import Announcement


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "organization",
        "audience",
        "priority",
        "is_published",
        "publish_at",
        "expires_at",
        "created_by",
        "created_at",
    )

    list_filter = (
        "organization",
        "audience",
        "priority",
        "is_published",
    )

    search_fields = (
        "title",
        "content",
        "organization__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "-created_at",
    )