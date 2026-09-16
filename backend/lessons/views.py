from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Lesson
from .serializers import (
    LessonSerializer,
    LessonCreateSerializer,
    LessonEditSerializer,
)

from django.utils import timezone
from .models import Lesson
from .serializers import LessonTeacherSerializer

from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
    get_user_teacher,
)

def scope_lessons_for_teacher(qs, user):
    """
    Teacher  → only lessons in their own classes.
    Admin    → only lessons in their org.
    Superuser→ all.
    """
    if user.is_superuser:
        return qs

    teacher = get_user_teacher(user)
    if teacher:
        return qs.filter(classroom__teacher=teacher)

    org = get_user_organization(user)
    if not org:
        return qs.none()
    return qs.filter(classroom__organization=org)


# ======================================================================
# Queryset helpers
# ======================================================================

def base_queryset():
    return (
        Lesson.objects
        .select_related(
            "classroom",
        )
    )


def queryset_for_user(user):
    """
    Superusers → all lessons.
    Admins     → only lessons belonging to their organization.
    """
    qs = base_queryset()
    if is_superuser(user):
        return qs

    org = get_user_organization(user)
    if not org:
        # Admin without an organization sees nothing.
        return qs.none()

    return qs.filter(classroom__organization=org)


def apply_filters(qs, request):
    """
    Apply optional query-string filters used by the frontend:

        ?status=this_week
        ?published=true|false
        ?year=2026
        ?week=5
        ?classroom=<id>
        ?teacher=<id>
        ?category=Creation
    """
    status_param = request.query_params.get("status")
    if status_param:
        qs = qs.filter(status=status_param)

    published = request.query_params.get("published")
    if published is not None:
        qs = qs.filter(published=published.lower() in ("1", "true", "yes"))

    year = request.query_params.get("year")
    if year:
        qs = qs.filter(year=year)

    week = request.query_params.get("week")
    if week:
        qs = qs.filter(week=week)

    classroom = request.query_params.get("classroom")
    if classroom:
        qs = qs.filter(classroom_id=classroom)

    category = request.query_params.get("category")
    if category:
        qs = qs.filter(category__iexact=category)

    return qs


# ======================================================================
# List + Create
# ======================================================================

class LessonListCreateAPIView(APIView):
    """
    GET  /lessons/
        List lessons visible to the current user.
        - Superuser → all lessons
        - Admin     → only lessons in their organization

    POST /lessons/
        Create a lesson. Superuser can create for any classroom;
        an admin can only create lessons inside their organization.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get(self, request):
        qs = queryset_for_user(request.user)
        qs = apply_filters(qs, request)

        serializer = LessonSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def post(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to create lessons.")

        serializer = LessonCreateSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Enforce organization scope on the write.
        self._check_org_scope(request.user, serializer.validated_data)

        lesson = serializer.save()

        response_serializer = LessonSerializer(
            lesson,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    # ------------------------------------------------------------------
    def _check_org_scope(self, user, data):
        """Admins can only write lessons inside their own organization."""
        if is_superuser(user):
            return

        org = get_user_organization(user)
        if not org:
            raise PermissionDenied("Your account is not linked to an organization.")

        classroom = data.get("classroom")
        if classroom and getattr(classroom, "organization_id", None) != org.id:
            raise PermissionDenied(
                "You can only create lessons for your own organization."
            )


# ======================================================================
# Detail: GET / PUT / PATCH / DELETE
# ======================================================================

class LessonDetailAPIView(APIView):
    """
    GET    /lessons/<id>/
    PUT    /lessons/<id>/
    PATCH  /lessons/<id>/
    DELETE /lessons/<id>/

    Superusers can manage any lesson.
    Admins can only read/manage lessons inside their organization.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get_object(self, request, pk):
        """
        Fetch a lesson the current user is allowed to see.
        Returns 404 (not 403) when out of scope so we don't leak
        the existence of other organizations' lessons.
        """
        qs = queryset_for_user(request.user)
        return get_object_or_404(qs, pk=pk)

    def _require_admin(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify lessons.")

    # ------------------------------------------------------------------
    def get(self, request, pk):
        lesson = self.get_object(request, pk)
        serializer = LessonSerializer(
            lesson,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def put(self, request, pk):
        self._require_admin(request)
        lesson = self.get_object(request, pk)

        serializer = LessonEditSerializer(
            lesson,
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self._check_org_scope(request.user, serializer.validated_data, lesson)

        lesson = serializer.save()

        response_serializer = LessonSerializer(
            lesson,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def patch(self, request, pk):
        self._require_admin(request)
        lesson = self.get_object(request, pk)

        serializer = LessonEditSerializer(
            lesson,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self._check_org_scope(request.user, serializer.validated_data, lesson)

        lesson = serializer.save()

        response_serializer = LessonSerializer(
            lesson,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def delete(self, request, pk):
        self._require_admin(request)
        lesson = self.get_object(request, pk)
        lesson.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # ------------------------------------------------------------------
    def _check_org_scope(self, user, data, instance):
        if is_superuser(user):
            return

        org = get_user_organization(user)
        if not org:
            raise PermissionDenied("Your account is not linked to an organization.")

        # Can't move a lesson into another organization.
        new_classroom = data.get("classroom", instance.classroom)
        if new_classroom and getattr(new_classroom, "organization_id", None) != org.id:
            raise PermissionDenied(
                "You can only manage lessons inside your own organization."
            )


# ======================================================================
# Frontend-specific actions
# ======================================================================

class LessonMakeThisWeekAPIView(APIView):
    """
    POST /lessons/<id>/make-this-week/
    Frontend: "Make this week" chip.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify lessons.")

        lesson = get_object_or_404(queryset_for_user(request.user), pk=pk)
        lesson.mark_this_week()

        serializer = LessonSerializer(
            lesson,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class LessonTogglePublishAPIView(APIView):
    """
    POST /lessons/<id>/toggle-publish/
    Frontend: "Publish" / "Hide" chip.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify lessons.")

        lesson = get_object_or_404(queryset_for_user(request.user), pk=pk)
        published = lesson.toggle_published()

        return Response(
            {"id": lesson.id, "published": published},
            status=status.HTTP_200_OK,
        )


class LessonSetDateAPIView(APIView):
    """
    POST /lessons/<id>/set-date/
    Frontend: "Set date" / "Save date" chip on the calendar.
    Body: { "lesson_date": "2026-09-21", "date_label": "September 21, 2026" }
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify lessons.")

        lesson = get_object_or_404(queryset_for_user(request.user), pk=pk)

        lesson_date = request.data.get("lesson_date")
        if not lesson_date:
            return Response(
                {"lesson_date": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        lesson.lesson_date = lesson_date
        lesson.date_label = request.data.get("date_label", "") or ""
        # `year` is synced inside Lesson.save().
        lesson.save(update_fields=["lesson_date", "date_label", "year", "updated_at"])

        serializer = LessonSerializer(
            lesson,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
class LessonTodayAPIView(APIView):
    """GET /lessons/today/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            Lesson.objects
            .select_related("classroom",)
            .order_by("lesson_date")       
        )
        qs = scope_lessons_for_teacher(qs, request.user)

        today = timezone.localdate()

        # 1. This week's lesson (explicit flag).
        this_week = (
            qs.filter(status=Lesson.STATUS_THIS_WEEK, published=True)
            .order_by("-lesson_date")
            .first()
        )

        # 2. Next upcoming lesson.
        upcoming = (
            qs.filter(published=True, lesson_date__gte=today)
            .exclude(status=Lesson.STATUS_COMPLETED)
            .order_by("lesson_date")          # ← removed "start_time"
            .first()
        )

        next_lesson = upcoming
        if this_week and upcoming and this_week.id == upcoming.id:
            next_lesson = (
                qs.filter(published=True, lesson_date__gt=upcoming.lesson_date)
                .order_by("lesson_date")      # ← removed "start_time"
                .first()
            )

        return Response({
            "lesson": (
                LessonTeacherSerializer(this_week, context={"request": request}).data
                if this_week else None
            ),
            "next": (
                LessonTeacherSerializer(next_lesson, context={"request": request}).data
                if next_lesson else None
            ),
        })


class LessonUpcomingAPIView(APIView):
    """GET /lessons/upcoming/?limit=10"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        limit = max(1, min(limit, 50))

        qs = (
            Lesson.objects
            .select_related("classroom")
            .filter(published=True)
            .order_by("lesson_date")          # ← removed "start_time"
        )
        qs = scope_lessons_for_teacher(qs, request.user)

        return Response(
            LessonTeacherSerializer(qs[:limit], many=True, context={"request": request}).data
        )

    