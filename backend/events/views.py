from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Event
from .serializers import (
    EventSerializer,
    EventCreateSerializer,
    EventEditSerializer,
)

from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
    get_user_teacher,
)

# ======================================================================
# Queryset helpers
# ======================================================================
def can_manage_events(user):
    return is_admin(user) or get_user_teacher(user) is not None

def base_queryset():
    return Event.objects.select_related("organization")


def queryset_for_user(user):
    """
    Superusers → all events.
    Admins     → only events belonging to their organization.
    Others     → nothing (parents will hit a separate read-only view).
    """
    qs = base_queryset()

    if is_superuser(user):
        return qs

    org = get_user_organization(user)
    if not org:
        return qs.none()

    return qs.filter(organization=org)


def apply_filters(qs, request):
    """
    Optional query-string filters used by the frontend:

        ?status=upcoming
        ?published=true|false
        ?event_type=service
        ?year=2026
        ?upcoming=true
    """
    status_param = request.query_params.get("status")
    if status_param:
        qs = qs.filter(status=status_param)

    published = request.query_params.get("published")
    if published is not None:
        qs = qs.filter(published=published.lower() in ("1", "true", "yes"))

    event_type = request.query_params.get("event_type")
    if event_type:
        qs = qs.filter(event_type=event_type)

    year = request.query_params.get("year")
    if year:
        qs = qs.filter(start_datetime__year=year)

    upcoming = request.query_params.get("upcoming")
    if upcoming and upcoming.lower() in ("1", "true", "yes"):
        from django.utils import timezone
        qs = qs.filter(start_datetime__gte=timezone.now())

    return qs


def enforce_org_scope(user, data, instance=None):
    """
    Ensure a non-superuser can only write events inside their org.

    `data` may contain an `organization` key (from the create/edit
    serializer). If absent, we fall back to the instance's org.
    """
    if is_superuser(user):
        return

    org = get_user_organization(user)
    if not org:
        raise PermissionDenied("Your account is not linked to an organization.")

    target_org = data.get("organization") or getattr(instance, "organization", None)
    if target_org and target_org.id != org.id:
        raise PermissionDenied(
            "You can only manage events inside your own organization."
        )


# ======================================================================
# List + Create  (superuser OR org-admin)
# ======================================================================

class EventListCreateAPIView(APIView):
    """
    GET  /events/
        Superuser → all events.
        Admin     → only events in their organization.

    POST /events/
        Create an event. The organization is injected from the
        authenticated user for non-superusers; superusers may pass
        `organization` explicitly.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get(self, request):
        qs = queryset_for_user(request.user)
        qs = apply_filters(qs, request)

        serializer = EventSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def post(self, request):
        if not can_manage_events(request.user):
            raise PermissionDenied("You do not have permission to create events.")

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

        serializer = EventCreateSerializer(
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

        event = serializer.save()

        # Record the creator when the model supports it.
        if hasattr(event, "created_by") and not event.created_by_id:
            event.created_by = request.user
            event.save(update_fields=["created_by", "updated_at"])

        response_serializer = EventSerializer(
            event,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ======================================================================
# Detail: GET / PUT / PATCH / DELETE
# ======================================================================

class EventDetailAPIView(APIView):
    """
    GET    /events/<id>/
    PUT    /events/<id>/
    PATCH  /events/<id>/
    DELETE /events/<id>/

    Superusers can manage any event.
    Admins can only read/manage events inside their organization.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get_object(self, request, pk):
        """
        Fetch an event the current user is allowed to see.
        Returns 404 (not 403) when out of scope so we don't leak the
        existence of other organizations' events.
        """
        qs = queryset_for_user(request.user)
        return get_object_or_404(qs, pk=pk)

    def _require_admin(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify events.")

    # ------------------------------------------------------------------
    def get(self, request, pk):
        event = self.get_object(request, pk)
        serializer = EventSerializer(
            event,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def put(self, request, pk):
        self._require_admin(request)
        event = self.get_object(request, pk)

        serializer = EventEditSerializer(
            event,
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, event)

        event = serializer.save()

        response_serializer = EventSerializer(
            event,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def patch(self, request, pk):
        self._require_admin(request)
        event = self.get_object(request, pk)

        serializer = EventEditSerializer(
            event,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, event)

        event = serializer.save()

        response_serializer = EventSerializer(
            event,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def delete(self, request, pk):
        self._require_admin(request)
        event = self.get_object(request, pk)
        event.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ======================================================================
# Frontend-specific actions
# ======================================================================

class EventTogglePublishAPIView(APIView):
    """
    POST /events/<id>/toggle-publish/
    Frontend: publish / hide chip.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify events.")

        event = get_object_or_404(queryset_for_user(request.user), pk=pk)
        published = event.toggle_published()

        return Response(
            {"id": event.id, "published": published},
            status=status.HTTP_200_OK,
        )
    