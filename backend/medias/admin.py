from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import Q

from .models import MediaItem

def thumb_html(url, size=40):
    """Small inline image preview for list_display."""
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;border-radius:6px;" />',
        url,
        size,
    )

# ======================================================================
# MediaItem admin
# ======================================================================

@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):

    org_field = "organization"

    list_display = (
        "title",
        "kind_badge",
        "organization",
        "source",
        "duration",
        "age_group",
        "youtube_id",
        "published_badge",
        "cover_preview",
    )
    list_filter = (
        "kind",
        "source",
        "published",
        "organization",
        "age_group",
    )
    search_fields = (
        "title",
        "description",
        "youtube_id",
        "file_name",
        "organization__name",
    )
    ordering = ("-created_at",)
    list_per_page = 25
    list_select_related = ("organization",)
    autocomplete_fields = ("organization",)
    readonly_fields = (
        "created_at",
        "updated_at",
        "file_name",
        "mime_type",
        "youtube_url",
    )

    fieldsets = (
        ("Identity", {
            "fields": ("title", "organization", "kind")
        }),
        ("Content", {
            "fields": ("description", "age_group", "duration")
        }),
        ("Source", {
            "fields": ("source", "youtube_id", "youtube_url")
        }),
        ("Files", {
            "fields": ("file", "cover", "file_name", "mime_type")
        }),
        ("Publishing", {
            "fields": ("published",)
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    actions = ("mark_published", "mark_unpublished")

    # ------------------------------------------------------------------
    @admin.display(description="Kind", ordering="kind")
    def kind_badge(self, obj):
        return obj.get_kind_display()

    @admin.display(description="Published", boolean=True)
    def published_badge(self, obj):
        return obj.published

    @admin.display(description="Cover")
    def cover_preview(self, obj):
        url = None
        if obj.cover:
            url = obj.cover.url
        elif obj.file and obj.kind == MediaItem.KIND_PICTURE:
            url = obj.file.url
        return thumb_html(url)

    @admin.display(description="YouTube URL")
    def youtube_url(self, obj):
        if not obj or not obj.youtube_id:
            return "—"
        return format_html(
            '<a href="{}" target="_blank">{}</a>',
            obj.youtube_url,
            obj.youtube_url,
        )

    # ------------------------------------------------------------------
    @admin.action(description="Publish selected media")
    def mark_published(self, request, queryset):
        updated = queryset.update(published=True)
        self.message_user(request, f"{updated} media item(s) published.")

    @admin.action(description="Unpublish selected media")
    def mark_unpublished(self, request, queryset):
        updated = queryset.update(published=False)
        self.message_user(request, f"{updated} media item(s) unpublished.")


# ======================================================================
# Admin site branding (optional)
# ======================================================================

admin.site.site_header = "Sunday School Admin"
admin.site.site_title = "Sunday School Admin"
admin.site.index_title = "Curriculum, events & media"