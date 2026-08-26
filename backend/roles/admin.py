from django.contrib import admin

from .models import Role, Permission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "codename",
        "category",
        "is_active",
        "created_at",
    )

    list_filter = (
        "category",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "codename",
        "category",
        "description",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "category",
        "name",
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "role_name",
        "is_active",
        "permission_count",
        "created_at",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    search_fields = (
        "role_name",
        "description",
    )

    filter_horizontal = (
        "permissions",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = (
        "role_name",
    )

    @admin.display(
        description="Permissions"
    )
    def permission_count(self, obj):
        return obj.permissions.count()