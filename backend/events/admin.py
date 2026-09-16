from django.contrib import admin
from .models import Event
from django.utils.html import format_html


def thumb_html(url, size=40):
    """Small inline image preview for list_display."""
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;border-radius:6px;" />',
        url,
        size,
    )

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    org_field = "organization"

    list_display = (
        "title",
        "organization",
        "event_type",
        "start_datetime",
        "end_datetime",
        "location",
        "audience",
        "status",
        "published_badge",
        "image_preview",
    )
    list_filter = (
        "status",
        "published",
        "event_type",
        "organization",
        ("start_datetime", admin.DateFieldListFilter),
    )
    search_fields = (
        "title",
        "description",
        "location",
        "audience",
        "organization__name",
    )
    date_hierarchy = "start_datetime"
    ordering = ("-start_datetime",)
    list_per_page = 25
    list_select_related = ("organization",)
    autocomplete_fields = ("organization",)
    readonly_fields = ("created_at", "updated_at", "display_date", "display_time")

    fieldsets = (
        ("Identity", {
            "fields": ("title", "organization", "event_type")
        }),
        ("When & where", {
            "fields": (
                "start_datetime",
                "end_datetime",
                "date_label",
                "time_label",
                "location",
            )
        }),
        ("Audience & content", {
            "fields": ("audience", "description")
        }),
        ("Media", {
            "fields": ("image",)
        }),
        ("Publishing", {
            "fields": ("status", "published")
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    actions = ("mark_published", "mark_unpublished", "mark_completed")

    # ------------------------------------------------------------------
    @admin.display(description="Published", boolean=True)
    def published_badge(self, obj):
        return obj.published

    @admin.display(description="Image")
    def image_preview(self, obj):
        return thumb_html(obj.image.url if obj.image else None)

    @admin.display(description="Display date")
    def display_date(self, obj):
        return obj.display_date if obj else "—"

    @admin.display(description="Display time")
    def display_time(self, obj):
        return obj.display_time if obj else "—"

    # ------------------------------------------------------------------
    @admin.action(description="Publish selected events")
    def mark_published(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f"{updated} event(s) published.")

    @admin.action(description="Unpublish selected events")
    def mark_unpublished(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f"{updated} event(s) unpublished.")

    @admin.action(description="Mark selected events as completed")
    def mark_completed(self, request, queryset):
        updated = queryset.update(status=Event.STATUS_COMPLETED)
        self.message_user(request, f"{updated} event(s) marked completed.")

