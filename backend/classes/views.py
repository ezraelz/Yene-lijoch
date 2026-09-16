from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import ClassRoom
from .serializers import (
    ClassRoomSerializer,
    ClassRoomCreateSerializer,
    ClassRoomEditSerializer,
)

from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
)

# ======================================================================
# Queryset helpers
# ======================================================================

def base_queryset():
    return (
        ClassRoom.objects
        .select_related("organization", "teacher__profile")
        .prefetch_related("roster")
    )


def queryset_for_user(user):
    """
    Superusers → all classes.
    Admins     → only classes inside their organization.
    Others     → only active classes inside their organization.
    """
    qs = base_queryset()

    if is_superuser(user):
        return qs

    org = get_user_organization(user)
    if not org:
        return qs.none()

    qs = qs.filter(organization=org)

    # Non-admins only see active groups.
    if not is_admin(user):
        qs = qs.filter(status=ClassRoom.STATUS_ACTIVE)

    return qs


def apply_filters(qs, request):
    """
    Optional query-string filters used by the frontend:

        ?status=active|inactive|completed
        ?teacher=<id>
        ?q=group (name search)
    """
    status_param = request.query_params.get("status")
    if status_param:
        qs = qs.filter(status=status_param)

    teacher = request.query_params.get("teacher")
    if teacher:
        qs = qs.filter(teacher_id=teacher)

    q = request.query_params.get("q")
    if q:
        qs = qs.filter(name__icontains=q)

    return qs


def enforce_org_scope(user, data, instance=None):
    """
    Ensure a non-superuser can only write classes inside their org.
    """
    if is_superuser(user):
        return

    org = get_user_organization(user)
    if not org:
        raise PermissionDenied("Your account is not linked to an organization.")

    target_org = data.get("organization") or getattr(instance, "organization", None)
    if target_org and target_org.id != org.id:
        raise PermissionDenied(
            "You can only manage groups inside your own organization."
        )


# ======================================================================
# List + Create
# ======================================================================

class ClassRoomListCreateAPIView(APIView):
    """
    GET  /classes/
        Superuser → all classes.
        Admin     → only classes in their organization.
        Other     → active classes only.

    POST /classes/
        Create a class (and optionally its nested students) in a single
        request, matching the AdminGroupsScreen's "Save group & students"
        button.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get(self, request):
        qs = queryset_for_user(request.user)
        qs = apply_filters(qs, request)

        serializer = ClassRoomSerializer(
            qs,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def post(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to create groups.")

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

        serializer = ClassRoomCreateSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": org,
                "created_by": request.user,
            },
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data)

        classroom = serializer.save()

        response_serializer = ClassRoomSerializer(
            classroom,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


# ======================================================================
# Detail: GET / PUT / PATCH / DELETE
# ======================================================================

class ClassRoomDetailAPIView(APIView):
    """
    GET    /classes/<id>/
    PUT    /classes/<id>/
    PATCH  /classes/<id>/
    DELETE /classes/<id>/

    Superusers can manage any class.
    Admins can only read/manage classes inside their organization.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # ------------------------------------------------------------------
    def get_object(self, request, pk):
        qs = queryset_for_user(request.user)
        return get_object_or_404(qs, pk=pk)

    def _require_admin(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify groups.")

    # ------------------------------------------------------------------
    def get(self, request, pk):
        classroom = self.get_object(request, pk)
        serializer = ClassRoomSerializer(
            classroom,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def put(self, request, pk):
        self._require_admin(request)
        classroom = self.get_object(request, pk)

        serializer = ClassRoomEditSerializer(
            classroom,
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, classroom)

        classroom = serializer.save()

        response_serializer = ClassRoomSerializer(
            classroom,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def patch(self, request, pk):
        self._require_admin(request)
        classroom = self.get_object(request, pk)

        serializer = ClassRoomEditSerializer(
            classroom,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        enforce_org_scope(request.user, serializer.validated_data, classroom)

        classroom = serializer.save()

        response_serializer = ClassRoomSerializer(
            classroom,
            context={"request": request},
        )
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    # ------------------------------------------------------------------
    def delete(self, request, pk):
        self._require_admin(request)
        classroom = self.get_object(request, pk)
        classroom.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ======================================================================
# Frontend-specific actions
# ======================================================================

class ClassRoomAddStudentAPIView(APIView):
    """
    POST /classes/<id>/students/
    Frontend: "Add student" chip on an existing group.
    Body matches the `addStudent({...})` payload.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from students.models import Student
        from students.serializers import StudentSerializer

        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify groups.")

        classroom = get_object_or_404(queryset_for_user(request.user), pk=pk)

        serializer = StudentSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": classroom.organization,
            },
        )

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        student = serializer.save(classroom=classroom)

        return Response(
            StudentSerializer(student, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ClassRoomRemoveStudentAPIView(APIView):
    """
    DELETE /classes/<id>/students/<student_id>/
    Frontend: "Remove" chip on a student row.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request, pk, student_id):
        from students.models import Student

        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify groups.")

        classroom = get_object_or_404(queryset_for_user(request.user), pk=pk)

        student = get_object_or_404(
            Student,
            pk=student_id,
            classroom=classroom,
        )
        student.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class ClassRoomDeactivateAPIView(APIView):
    """
    POST /classes/<id>/deactivate/
    Frontend: soft-delete equivalent. Preserves the group + students,
    just flips the status to 'inactive'.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to modify groups.")

        classroom = get_object_or_404(queryset_for_user(request.user), pk=pk)
        classroom.status = ClassRoom.STATUS_INACTIVE
        classroom.save(update_fields=["status", "updated_at"])

        return Response(
            {"id": classroom.id, "status": classroom.status},
            status=status.HTTP_200_OK,
        )
    