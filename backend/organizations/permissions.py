from rest_framework.permissions import BasePermission


class IsSuperUser(BasePermission):
    """Only superusers may approve/reject organizations or memberships."""
    message = "Only a superuser can perform this action."

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


class IsAuthenticatedAndActive(BasePermission):
    message = "You must be signed in with an active account."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and getattr(request.user, "is_active", True)
        )
    