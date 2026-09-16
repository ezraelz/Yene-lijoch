from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from .models import Teacher
from .serializers import (
    TeacherSerializer,
    TeacherMeSerializer,
    TeacherCreateSerializer,
    TeacherRegisterSerializer,
    TeacherEditSerializer,
)
from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
)


# ======================================================================
# Scoping helpers (same pattern as everywhere else)
# ======================================================================

def base_queryset():
    return (
        Teacher.objects
        .select_related("profile", "profile__organization")
        .prefetch_related("classes")
    )


def queryset_for_user(user):
    qs = base_queryset()
    if is_superuser(user):
        return qs
    org = get_user_organization(user)
    if not org:
        return qs.none()
    return qs.filter(profile__organization__organization=org)


# ======================================================================
# Me — the endpoint TeacherContext depends on
# ======================================================================

class TeacherMeAPIView(APIView):
    """GET /teachers/me/"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        teacher = get_object_or_404(
            base_queryset(),
            profile=request.user,
        )
        return Response(TeacherMeSerializer(teacher).data)


# ======================================================================
# List + create
# ======================================================================

class TeacherListCreateAPIView(APIView):
    """
    GET  /teachers/
    POST /teachers/     (register a new teacher + profile)
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        qs = queryset_for_user(request.user)
        return Response(TeacherSerializer(qs, many=True).data)

    def post(self, request):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to register teachers.")

        serializer = TeacherRegisterSerializer(
            data=request.data,
            context={
                "request": request,
                "organization": get_user_organization(request.user),
            },
        )
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()

        teacher = profile.teacher_profile
        return Response(
            TeacherSerializer(teacher).data,
            status=status.HTTP_201_CREATED,
        )


# ======================================================================
# Detail
# ======================================================================

class TeacherDetailAPIView(APIView):
    """
    GET    /teachers/<id>/
    PATCH  /teachers/<id>/
    DELETE /teachers/<id>/
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_object(self, request, pk):
        qs = queryset_for_user(request.user)
        return get_object_or_404(qs, pk=pk)

    def get(self, request, pk):
        return Response(TeacherSerializer(self.get_object(request, pk)).data)

    def patch(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to edit teachers.")

        teacher = self.get_object(request, pk)
        serializer = TeacherEditSerializer(
            teacher,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        return Response(TeacherSerializer(teacher).data)

    def delete(self, request, pk):
        if not is_admin(request.user):
            raise PermissionDenied("You do not have permission to delete teachers.")
        self.get_object(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    