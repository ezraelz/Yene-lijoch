from django.db import connection
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from organizations.models import Organization
from .models import Student
from .serializers import (
    StudentSerializer,
    StudentEditSerializer,
    StudentRegisterSerializer,
    StudentCreateSerializer,
    StudentSearchSerializer,
    StudentSummarySerializer,
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

def can_manage_students(user):
    """Admins and teachers can create/edit students."""
    return is_admin(user) or get_user_teacher(user) is not None

def base_queryset():
    return (
        Student.objects
        .select_related(
            "profile",
            "profile__organization",
            "classroom",
            "organization",
        )
    )


def queryset_for_user(user):
    """
    Superusers → all students.
    Admins     → only students in their organization (all statuses).
    Others     → only active students in their organization.
    """
    qs = base_queryset()

    if is_superuser(user):
        return qs

    org = get_user_organization(user)
    if not org:
        return qs.none()

    qs = qs.filter(organization=org)

    # Non-admins only see active students.
    if not is_admin(user):
        qs = qs.filter(status=Student.STATUS_ACTIVE)

    return qs


def apply_filters(qs, request):
    """
    Optional query-string filters used by the frontend:

        ?status=active|inactive|graduated
        ?classroom=<id>
        ?q=search
    """
    status_param = request.query_params.get("status")
    if status_param:
        qs = qs.filter(status=status_param)

    classroom = request.query_params.get("classroom")
    if classroom:
        qs = qs.filter(classroom_id=classroom)

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(profile__first_name__icontains=q) | qs.filter(
            profile__last_name__icontains=q
        )

    return qs


def enforce_org_scope(user, data, instance=None):
    """
    Ensure a non-superuser can only write students inside their org.
    """
    if is_superuser(user):
        return

    org = get_user_organization(user)
    if not org:
        raise PermissionDenied("Your account is not linked to an organization.")

    target_org = data.get("organization") or getattr(instance, "organization", None)
    if target_org and target_org.id != org.id:
        raise PermissionDenied(
            "You can only manage students inside your own organization."
        )


# ======================================================================
# Search
# ======================================================================

class StudentSearchView(APIView):
    """
    GET /api/students/search/?q=...
    Public read endpoint for duplicate-checking / lookups.
    """

    permission_classes = []
    authentication_classes = []

    def get(self, request):
        serializer = StudentSearchSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        q = serializer.validated_data["q"]

        qs = Student.objects.select_related("profile")

        if connection.vendor == "postgresql":
            from django.contrib.postgres.search import TrigramSimilarity

            results = (
                qs.filter(profile__first_name__icontains=q)
                .annotate(similarity=TrigramSimilarity("profile__first_name", q))
                .filter(similarity__gt=0.15)
                .order_by("-similarity")[:10]
            )
        else:
            results = qs.filter(profile__first_name__icontains=q)[:10]

        return Response(
            StudentSummarySerializer(results, many=True).data,
            status=status.HTTP_200_OK,
        )


# ======================================================================
# List + Create
# ======================================================================

class StudentListCreateAPIView(APIView):
    """
    GET  /students/
        Superuser → all students.
        Admin     → only students in their organization.
        Other     → active students only.

    POST /students/
        Create a student. The organization is injected from the
        authenticated user; superusers may pass `organization` in the
        body.

        Accepts the full frontend payload:
            { name, groupId, grade, age, parentName, parentEmail }
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get(self, request):
        qs = queryset_for_user(request.user)
        qs = apply_filters(qs, request)

        serializer = StudentSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def post(self, request):
        if not can_manage_students(request.user):
            raise PermissionDenied("You do not have permission to create students.")

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

        serializer = StudentCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": org,
            },
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data)

        student = serializer.save()

        response_serializer = StudentSerializer(
            student,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ======================================================================
# Detail: GET / PUT / PATCH / DELETE
# ======================================================================

class StudentDetailAPIView(APIView):
    """
    GET    /students/<id>/
    PUT    /students/<id>/
    PATCH  /students/<id>/
    DELETE /students/<id>/

    Superusers can manage any student.
    Admins can only read/manage students inside their organization.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get_object(self, request, pk):
        qs = queryset_for_user(request.user)
        return get_object_or_404(qs, pk=pk)

    def _require_admin(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify students.")

    # ------------------------------------------------------------------
    def get(self, request, pk):
        student = self.get_object(request, pk)
        serializer = StudentSerializer(
            student,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def put(self, request, pk):
        self._require_admin(request)
        student = self.get_object(request, pk)

        serializer = StudentEditSerializer(
            student,
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, student)

        student = serializer.save()

        response_serializer = StudentSerializer(
            student,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def patch(self, request, pk):
        self._require_admin(request)
        student = self.get_object(request, pk)

        serializer = StudentEditSerializer(
            student,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, student)

        student = serializer.save()

        response_serializer = StudentSerializer(
            student,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def delete(self, request, pk):
        """
        Soft delete: flips status to 'inactive' and deactivates the
        linked Profile. The Student row is preserved.
        """
        self._require_admin(request)
        student = self.get_object(request, pk)

        student.status = Student.STATUS_INACTIVE
        student.profile.is_active = False
        student.profile.save(update_fields=["is_active"])
        student.save(update_fields=["status", "updated_at"])

        return Response(
            {"detail": "Student deactivated successfully."},
            status=status.HTTP_200_OK,
        )


# ======================================================================
# Frontend-specific action: register via Profile + Student
# ======================================================================

class StudentRegisterAPIView(APIView):
    """
    POST /students/register/
    Full registration — creates a Profile *and* a Student in one call.
    Body matches the StudentRegisterSerializer (which nests
    student_details as a StudentCreateSerializer).
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to register students.")

        if is_superuser(request.user):
            org = request.data.get("organization") or None
        else:
            org = get_user_organization(request.user)

        if not org:
            return Response(
                {"detail": "You are not associated with an organization."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = StudentRegisterSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": org,
            },
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student = serializer.save()

        response_serializer = StudentSerializer(
            student,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    