from django.urls import path

from .views import (
    # Roles
    RoleView,
    RoleDetailView,
    RoleStatsView,
    RoleCopyView,

    # Permissions
    PermissionView,
    PermissionDetailView,
    PermissionCategoryView,
    PermissionBulkDeleteView,
    PermissionValidateView,
    PermissionExportView,
    PermissionImportView,
)


urlpatterns = [

    # ========================================================
    # ROLES
    # ========================================================

    path(
        "roles/",
        RoleView.as_view(),
        name="roles",
    ),

    path(
        "roles/stats/",
        RoleStatsView.as_view(),
        name="role-stats",
    ),

    path(
        "roles/<int:pk>/copy/",
        RoleCopyView.as_view(),
        name="role-copy",
    ),

    path(
        "roles/<int:pk>/",
        RoleDetailView.as_view(),
        name="role-detail",
    ),


    # ========================================================
    # PERMISSIONS
    # ========================================================

    # List + create
    path(
        "permissions/",
        PermissionView.as_view(),
        name="permissions",
    ),

    # Categories
    path(
        "permissions/category/",
        PermissionCategoryView.as_view(),
        name="permission-categories",
    ),

    # Validate codename
    path(
        "permissions/validate/",
        PermissionValidateView.as_view(),
        name="permission-validate",
    ),

    # Export CSV
    path(
        "permissions/export/",
        PermissionExportView.as_view(),
        name="permission-export",
    ),

    # Import CSV
    path(
        "permissions/import/",
        PermissionImportView.as_view(),
        name="permission-import",
    ),

    # Bulk delete
    #
    # Example:
    # DELETE /permissions/1,2,3/bulk/
    path(
        "permissions/<path:ids>/bulk/",
        PermissionBulkDeleteView.as_view(),
        name="permission-bulk-delete",
    ),

    # Detail
    path(
        "permissions/<int:pk>/",
        PermissionDetailView.as_view(),
        name="permission-detail",
    ),
]
