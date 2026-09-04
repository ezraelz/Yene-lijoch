from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "title",
        "organization__name",
        "event_type",
        "location",
        "start_datetime",
        "end_datetime",
        "status",
    )

    list_filter = (
        "organization",
        "event_type",
        "status",
        "start_datetime",
    )

    search_fields = (
        "title",
        "description",
        "location",
        "organization__name",
    )

    date_hierarchy = "start_datetime"

    ordering = (
        "-start_datetime",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Event Information",
            {
                "fields": (
                    "organization__name",
                    "title",
                    "description",
                    "event_type",
                    "status",
                )
            }
        ),

        (
            "Schedule",
            {
                "fields": (
                    "start_datetime",
                    "end_datetime",
                    "location",
                )
            }
        ),

        (
            "Image",
            {
                "fields": (
                    "image",
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
