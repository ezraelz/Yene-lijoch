from django.contrib import admin
from django.utils.html import format_html
from .models import Lesson


def thumb_html(url, size=40):
    """Small inline image preview for list_display."""
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;border-radius:6px;" />',
        url,
        size,
    )

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):

    # The Lesson model is scoped via its classroom's organization.
    org_field = "classroom__organization"

    list_display = (
        "title",
        "week_badge",
        "category",
        "classroom",
        "lesson_date",
        "status",
        "published_badge",
        "cover_preview",
    )
    list_filter = (
        "status",
        "published",
        "category",
        "year",
        "week",
        "classroom",
    )
    search_fields = (
        "title",
        "scripture",
        "memory_verse",
        "description",
        "classroom__name",
    )
    date_hierarchy = "lesson_date"
    ordering = ("-lesson_date", "-week")
    list_per_page = 25
    list_select_related = ("classroom", )
    autocomplete_fields = ("classroom", )
    readonly_fields = ("created_at", "updated_at", "display_date", "slug")

    fieldsets = (
        ("Identity", {
            "fields": ("title", "category", "week", "classroom")
        }),
        ("Schedule", {
            "fields": ("lesson_date", "year", "date_label", )
        }),
        ("Content", {
            "fields": ("scripture", "memory_verse", "description")
        }),
        ("Media", {
            "fields": ("cover", "attachment", "attachment_name", "attachment_type")
        }),
        ("Publishing", {
            "fields": ("status", "published")
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    actions = ("make_this_week", "publish_selected", "unpublish_selected")

    # ------------------------------------------------------------------
    # List display helpers
    # ------------------------------------------------------------------
    @admin.display(description="Week", ordering="week")
    def week_badge(self, obj):
        return f"W{obj.week}"

    @admin.display(description="Published", boolean=True)
    def published_badge(self, obj):
        return obj.published

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        return thumb_html(obj.cover.url if obj.cover else None)

    @admin.display(description="Display date")
    def display_date(self, obj):
        return obj.display_date if obj else "—"

    # ------------------------------------------------------------------
    # Bulk actions
    # ------------------------------------------------------------------
    @admin.action(description="Mark as this week's lesson")
    def make_this_week(self, request, queryset):
        # Only one lesson can be "this week" per scope.
        queryset.update(status=Lesson.STATUS_UPCOMING)
        updated = 0
        for lesson in queryset:
            lesson.mark_this_week()
            updated += 1
        self.message_user(request, f"{updated} lesson(s) marked as this week.")

    @admin.action(description="Publish selected lessons")
    def publish_selected(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f"{updated} lesson(s) published.")

    @admin.action(description="Unpublish selected lessons")
    def unpublish_selected(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f"{updated} lesson(s) unpublished.")


