from django.db.models import Prefetch

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Teacher
from .serializers import (
    TeacherSerializer,
    TeacherEditSerializer,
    TeacherRegisterSerializer,
)


class TeacherListCreateAPIView(APIView):
    """
    GET  /teachers/
        List all teachers.

    POST /teachers/
        Register a new teacher including Profile information.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):
        teachers = (
            Teacher.objects
            .select_related("profile", "organization")
            .prefetch_related("subject")
            .order_by("id")
        )

        serializer = TeacherSerializer(
            teachers,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = TeacherRegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():
            profile = serializer.save()

            # Get the newly created teacher
            teacher = profile.teacher_profile

            response_serializer = TeacherSerializer(
                teacher
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class TeacherDetailAPIView(APIView):
    """
    GET    /teachers/<id>/    Retrieve teacher.
    PUT    /teachers/<id>/    Update teacher.
    PATCH  /teachers/<id>/    Partially update teacher.
    DELETE /teachers/<id>/    Delete teacher.
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return (
                Teacher.objects
                .select_related("profile", "organization")
                .prefetch_related("subject")
                .get(pk=pk)
            )
        except Teacher.DoesNotExist:
            return None

    def get(self, request, pk):
        teacher = self.get_object(pk)

        if teacher is None:
            return Response(
                {
                    "detail": "Teacher not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeacherSerializer(
            teacher
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        teacher = self.get_object(pk)

        if teacher is None:
            return Response(
                {
                    "detail": "Teacher not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeacherEditSerializer(
            teacher,
            data=request.data
        )

        if serializer.is_valid():
            teacher = serializer.save()

            response_serializer = TeacherSerializer(
                teacher
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        teacher = self.get_object(pk)

        if teacher is None:
            return Response(
                {
                    "detail": "Teacher not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = TeacherEditSerializer(
            teacher,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            teacher = serializer.save()

            response_serializer = TeacherSerializer(
                teacher
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        teacher = self.get_object(pk)

        if teacher is None:
            return Response(
                {
                    "detail": "Teacher not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        teacher.delete()

        return Response(
            {
                "detail": "Teacher deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
    