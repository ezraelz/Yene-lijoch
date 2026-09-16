from rest_framework.permissions import BasePermission


class IsOrgAdminUser(BasePermission):
    """Only organization admin users to access student data of thier org."""
    message = "Only a organization admins can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role.role_name == "admin")


class IsAuthenticatedAndActive(BasePermission):
    message = "You must be signed in with an active account."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_active", True)
        )
    