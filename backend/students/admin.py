from django.contrib import admin
from django.utils.html import format_html

from .models import Student


def thumb_html(url, size=40):
    if not url:
        return "—"
    return format_html(
        '<img src="{}" style="height:{}px;width:{}px;'
        'border-radius:50%;object-fit:cover;" />',
        url,
        size,
        size,
    )


# ======================================================================
# Student admin
# ======================================================================

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):

    # ------------------------------------------------------------------
    # List view
    # ------------------------------------------------------------------
    list_display = (
        "id",
        "avatar_preview",
        "get_student_name",
        "get_username",
        "grade",
        "age",
        "group_name",
        "guardian_name",
        "guardian_email",
        "guardian_contact",
        "status_badge",
        "enrollment_date",
    )

    list_display_links = ("id", "get_student_name")

    list_filter = (
        "status",
        "grade",
        "organization",
        "classroom",
        ("enrollment_date", admin.DateFieldListFilter),
    )

    search_fields = (
        "profile__username",
        "profile__first_name",
        "profile__last_name",
        "profile__email",
        "guardian_name",
        "guardian_email",
        "guardian_contact",
        "classroom__name",
        "organization__name",
    )

    ordering = ("profile__first_name", "profile__last_name")

    list_per_page = 25

    list_select_related = (
        "profile",
        "profile__organization",
        "classroom",
        "organization",
    )

    autocomplete_fields = ("profile", "classroom", "organization")

    readonly_fields = (
        "created_at",
        "updated_at",
        "full_name_display",
        "group_name_display",
        "profile_link",
    )

    # ------------------------------------------------------------------
    # Form layout
    # ------------------------------------------------------------------
    fieldsets = (
        ("Identity", {
            "fields": ("profile", "profile_link", "full_name_display")
        }),
        ("Enrollment", {
            "fields": (
                "organization",
                "classroom",
                "group_name_display",
                "grade",
                "age",
                "status",
                "enrollment_date",
            )
        }),
        ("Guardian", {
            "fields": ("guardian_name", "guardian_email", "guardian_contact")
        }),
        ("Meta", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    actions = ("mark_active", "mark_inactive", "mark_graduated")

    # ==================================================================
    # List display helpers
    # ==================================================================

    @admin.display(description="")
    def avatar_preview(self, obj):
        img = getattr(obj.profile, "profile_image", None) if obj.profile else None
        if not img:
            return "—"
        try:
            return thumb_html(img.url)
        except ValueError:
            return "—"

    @admin.display(description="Student Name", ordering="profile__first_name")
    def get_student_name(self, obj):
        if not obj.profile:
            return obj.guardian_name or "—"
        return (
            f"{obj.profile.first_name or ''} "
            f"{obj.profile.last_name or ''}"
        ).strip() or "—"

    @admin.display(description="Username", ordering="profile__username")
    def get_username(self, obj):
        return getattr(obj.profile, "username", "") or "—"

    @admin.display(description="Group", ordering="classroom__name")
    def group_name(self, obj):
        return obj.classroom.name if obj.classroom_id else "—"

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        colors = {
            Student.STATUS_ACTIVE: "#1B873F",
            Student.STATUS_INACTIVE: "#B00020",
            Student.STATUS_GRADUATED: "#0B72B9",
        }
        color = colors.get(obj.status, "#666")
        return format_html(
            '<span style="background:{};color:#fff;'
            'padding:2px 8px;border-radius:10px;font-size:11px;">{}</span>',
            color,
            obj.get_status_display() if obj.status else "—",
        )

    # ==================================================================
    # Read-only helpers (shown on the detail page)
    # ==================================================================

    @admin.display(description="Full name")
    def full_name_display(self, obj):
        return obj.full_name or "—"

    @admin.display(description="Group")
    def group_name_display(self, obj):
        return obj.group_name or "—"

    @admin.display(description="Profile")
    def profile_link(self, obj):
        if not obj.profile_id:
            return "—"
        return format_html(
            '<a href="/admin/users/profile/{}/change/">Open profile</a>',
            obj.profile_id,
        )

    # ==================================================================
    # Bulk actions
    # ==================================================================

    @admin.action(description="Mark selected students as active")
    def mark_active(self, request, queryset):
        updated = queryset.update(status=Student.STATUS_ACTIVE)
        self.message_user(request, f"{updated} student(s) marked active.")

    @admin.action(description="Mark selected students as inactive")
    def mark_inactive(self, request, queryset):
        # Also deactivate the linked Profile.
        updated = queryset.update(status=Student.STATUS_INACTIVE)
        queryset.update(profile__is_active=False)  # not valid; see below
        # Use an explicit loop because `.update()` can't cross relations.
        for student in queryset.select_related("profile"):
            student.profile.is_active = False
            student.profile.save(update_fields=["is_active"])
        self.message_user(request, f"{updated} student(s) marked inactive.")

    @admin.action(description="Mark selected students as graduated")
    def mark_graduated(self, request, queryset):
        updated = queryset.update(status=Student.STATUS_GRADUATED)
        self.message_user(request, f"{updated} student(s) marked graduated.")
