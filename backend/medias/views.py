from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import MediaItem
from .serializers import (
    MediaItemSerializer,
    MediaItemCreateSerializer,
    MediaItemEditSerializer,
)


# ======================================================================
# Permission helpers
# ======================================================================

def is_superuser(user):
    return bool(user and user.is_authenticated and user.is_superuser)


def is_admin(user):
    """
    Any staff user is treated as an 'admin'. Swap for a group / role
    check (e.g. user.groups.filter(name="OrgAdmin").exists()) if you
    have a dedicated OrgAdmin role.
    """
    return bool(user and user.is_authenticated and user.is_staff)


def get_user_organization(user):
    """
    Return the `Organization` the user belongs to, or None for superusers.

    `request.user` is a Profile (AUTH_USER_MODEL = users.Profile), so the
    membership is at `user.organization`. If a raw auth.User is passed
    (e.g. from the admin), fall back to `user.profile.organization`.

    Always unwraps OrganizationMembership → Organization.
    """
    if not user or not user.is_authenticated:
        return None
    if getattr(user, "is_superuser", False):
        return None

    # Case A: user is a Profile (the normal case for API requests).
    membership = getattr(user, "organization", None)

    # Case B: user is an auth.User with a .profile (admin site, shell).
    if membership is None:
        profile = getattr(user, "profile", None)
        if profile:
            membership = getattr(profile, "organization", None)

    if not membership:
        return None

    # If it's already an Organization, return it. If it's a membership,
    # unwrap to the underlying Organization.
    return getattr(membership, "organization", membership)


# ======================================================================
# Queryset helpers
# ======================================================================

def base_queryset():
    return MediaItem.objects.select_related("organization")


def queryset_for_user(user):
    """
    Superusers → all media.
    Admins     → only media inside their organization.
    Others     → only their organization's *published* media.
    """
    qs = base_queryset()

    if is_superuser(user):
        return qs

    org = get_user_organization(user)
    if not org:
        return qs.none()

    qs = qs.filter(organization=org)

    # Non-admins only see published items.
    if not is_admin(user):
        qs = qs.filter(published=True)

    return qs


def apply_filters(qs, request):
    """
    Optional query-string filters used by the frontend:

        ?kind=video|song|bible_story|course|picture
        ?source=gallery|youtube
        ?published=true|false
        ?age_group=Ages 5–10
        ?q=noah
    """
    kind = request.query_params.get("kind")
    if kind:
        qs = qs.filter(kind=kind)

    source = request.query_params.get("source")
    if source:
        qs = qs.filter(source=source)

    published = request.query_params.get("published")
    if published is not None:
        qs = qs.filter(published=published.lower() in ("1", "true", "yes"))

    age_group = request.query_params.get("age_group")
    if age_group:
        qs = qs.filter(age_group__iexact=age_group)

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(title__icontains=q)

    return qs


def enforce_org_scope(user, data, instance=None):
    """
    Ensure a non-superuser can only write media inside their org.
    """
    if is_superuser(user):
        return

    org = get_user_organization(user)
    if not org:
        raise PermissionDenied("Your account is not linked to an organization.")

    target_org = data.get("organization") or getattr(instance, "organization", None)
    if target_org and target_org.id != org.id:
        raise PermissionDenied(
            "You can only manage media inside your own organization."
        )


# ======================================================================
# List + Create
# ======================================================================

class MediaItemListCreateAPIView(APIView):
    """
    GET  /media/
        Superuser → all media.
        Admin     → only media in their organization.
        Parent    → only published media in their organization.

    POST /media/
        Create a media item. The organization is injected from the
        authenticated user for non-superusers; superusers may pass
        `organization` explicitly.

        Accepts multipart/form-data so `file` and `cover` can be
        uploaded alongside the JSON-ish metadata fields.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get(self, request):
        qs = queryset_for_user(request.user)
        qs = apply_filters(qs, request)

        serializer = MediaItemSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def post(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to upload media.")

        # Determine the target organization.
        if is_superuser(request.user):
            org = request.data.get("organization") or None
        else:
            org = get_user_organization(request.user)
            if not org:
                return Response(
                    {"detail": "You are not associated with an organization."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        serializer = MediaItemCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": org,
            },
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Guard: non-superusers can only write inside their own org.
        enforce_org_scope(request.user, serializer.validated_data)

        # Inject the resolved organization.
        media = serializer.save(organization=org) if org else serializer.save()

        # Record the creator when the model supports it.
        if hasattr(media, "created_by") and not media.created_by_id:
            media.created_by = request.user
            media.save(update_fields=["created_by", "updated_at"])

        response_serializer = MediaItemSerializer(
            media,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ======================================================================
# Detail: GET / PUT / PATCH / DELETE
# ======================================================================

class MediaItemDetailAPIView(APIView):
    """
    GET    /media/<id>/
    PUT    /media/<id>/
    PATCH  /media/<id>/
    DELETE /media/<id>/

    Superusers can manage any media item.
    Admins can only read/manage media inside their organization.
    Parents can only read published media inside their organization.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get_object(self, request, pk):
        """
        Fetch a media item the current user is allowed to see.
        Returns 404 (not 403) when out of scope so we don't leak the
        existence of other organizations' media.
        """
        qs = queryset_for_user(request.user)
        return get_object_or_404(qs, pk=pk)

    def _require_admin(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify media.")

    # ------------------------------------------------------------------
    def get(self, request, pk):
        media = self.get_object(request, pk)
        serializer = MediaItemSerializer(
            media,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def put(self, request, pk):
        self._require_admin(request)
        media = self.get_object(request, pk)

        serializer = MediaItemEditSerializer(
            media,
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, media)

        media = serializer.save()

        response_serializer = MediaItemSerializer(
            media,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def patch(self, request, pk):
        self._require_admin(request)
        media = self.get_object(request, pk)

        serializer = MediaItemEditSerializer(
            media,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, media)

        media = serializer.save()

        response_serializer = MediaItemSerializer(
            media,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def delete(self, request, pk):
        self._require_admin(request)
        media = self.get_object(request, pk)
        media.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ======================================================================
# Frontend-specific actions
# ======================================================================

class MediaItemTogglePublishAPIView(APIView):
    """
    POST /media/<id>/toggle-publish/
    Frontend: publish / hide chip.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify media.")

        media = get_object_or_404(queryset_for_user(request.user), pk=pk)
        published = media.toggle_published()

        return Response(
            {"id": media.id, "published": published},
            status=status.HTTP_200_OK,
        )
    