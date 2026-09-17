from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from .models import Parent
from .serializers import (
    ParentSerializer,
    ParentEditSerializer,
    ParentRegisterSerializer,
    ParentMeSerializer
)
from .permissions import IsParentUser
from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
)

# ======================================================================
# Scope helpers
# ======================================================================

def base_queryset():
    return (
        Parent.objects
        .select_related("profile", "organization")
        .prefetch_related("student__profile")
    )


def queryset_for_user(user):
    """
    Superuser → all.
    Admin     → parents in their org.
    Parent    → only themselves.
    """
    qs = base_queryset()
    if is_superuser(user):
        return qs

    if is_admin(user):
        org = get_user_organization(user)
        if not org:
            return qs.none()
        return qs.filter(organization=org)

    # Parents see only their own record.
    return qs.filter(profile=user)


# ======================================================================
# List + create
# ======================================================================

class ParentListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = queryset_for_user(request.user)
        return Response(
            ParentSerializer(qs, many=True, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        if not (is_admin(request.user) or is_superuser(request.user)):
            raise PermissionDenied("Only admins can register parents.")

        serializer = ParentRegisterSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": get_user_organization(request.user),
            },
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        profile = serializer.save()
        parent = profile.parent_profile
        return Response(
            ParentSerializer(parent, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


# ======================================================================
# Detail
# ======================================================================

class ParentDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        return get_object_or_404(queryset_for_user(request.user), pk=pk)

    def _require_admin(self, request):
        if not (is_admin(request.user) or is_superuser(request.user)):
            raise PermissionDenied("Admin access required.")

    def get(self, request, pk):
        parent = self.get_object(request, pk)
        return Response(
            ParentSerializer(parent, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request, pk):
        self._require_admin(request)
        parent = self.get_object(request, pk)
        serializer = ParentEditSerializer(parent, data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        parent = serializer.save()
        return Response(ParentSerializer(parent, context={"request": request}).data)

    def patch(self, request, pk):
        self._require_admin(request)
        parent = self.get_object(request, pk)
        serializer = ParentEditSerializer(parent, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        parent = serializer.save()
        return Response(ParentSerializer(parent, context={"request": request}).data)

    def delete(self, request, pk):
        self._require_admin(request)
        self.get_object(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ======================================================================
# Me — the parent's own profile
# ======================================================================

class ParentMeView(APIView):
    permission_classes = [IsAuthenticated, IsParentUser]

    def get_object(self, request):
        # request.user IS the Profile, so filter by it directly.
        return get_object_or_404(
            Parent.objects.select_related("profile"),
            profile=request.user,
        )

    def get(self, request):
        parent = self.get_object(request)
        return Response(
            ParentMeSerializer(parent, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def put(self, request):
        # BUG FIX: was passing `user` (a Profile) instead of the Parent row.
        parent = self.get_object(request)
        serializer = ParentEditSerializer(parent, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        parent = serializer.save()
        return Response(
            ParentSerializer(parent, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )

    def delete(self, request):
        # Soft-deactivate both the Parent row (if it has a status) and
        # the underlying Profile.
        parent = self.get_object(request)
        profile = parent.profile
        profile.is_active = False
        profile.save(update_fields=["is_active"])

        if hasattr(parent, "status"):
            parent.status = "inactive"
            parent.save(update_fields=["status"])

        return Response(
            {"detail": "Your account has been deactivated."},
            status=status.HTTP_200_OK,
        )


# ======================================================================
# Admin: parents in the caller's org
# ======================================================================

class AdminParentView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not (is_admin(request.user) or is_superuser(request.user)):
            raise PermissionDenied("Admin access required.")

        qs = queryset_for_user(request.user).filter(
            profile__role__role_name="parent"
        )

        try:
            limit = int(request.query_params.get("limit", 50))
        except (TypeError, ValueError):
            limit = 50
        limit = max(1, min(limit, 200))

        return Response(
            ParentSerializer(qs[:limit], many=True, context={"request": request}).data,
            status=status.HTTP_200_OK,
        )