from rest_framework.permissions import BasePermission

class IsParentUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.role_name == "parent")


class IsOrgAdminUser(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.role_name == "admin")

