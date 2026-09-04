from django.db.models import Prefetch

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Student
from .serializers import (
    StudentSerializer,
    StudentEditSerializer,
    StudentRegisterSerializer,
)

class StudentListCreateAPIView(APIView):
    """
    GET  /students/
        List all students.

    POST /students/
        Register a new student.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        students = (
            Student.objects
            .select_related("profile", "organization")
            .order_by("id")
        )

        serializer = StudentSerializer(
            students,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = StudentRegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            profile = serializer.save()

            # Get created student
            student = profile.student_profile

            response_serializer = StudentSerializer(
                student
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class StudentDetailAPIView(APIView):
    """
    GET    /students/<id>/
    PUT    /students/<id>/
    PATCH  /students/<id>/
    DELETE /students/<id>/
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return (
                Student.objects
                .select_related("profile", "organization")
                .get(pk=pk)
            )

        except Student.DoesNotExist:
            return None

    def get(self, request, pk):

        student = self.get_object(pk)

        if student is None:
            return Response(
                {
                    "detail": "Student not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentSerializer(
            student
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):

        student = self.get_object(pk)

        if student is None:
            return Response(
                {
                    "detail": "Student not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentEditSerializer(
            student,
            data=request.data
        )

        if serializer.is_valid():

            student = serializer.save()

            response_serializer = StudentSerializer(
                student
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

        student = self.get_object(pk)

        if student is None:
            return Response(
                {
                    "detail": "Student not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = StudentEditSerializer(student,data=request.data,partial=True)
        print(request.data, 'request data');
        if serializer.is_valid():
            serializer.save()
            print(serializer.data, 'response data')
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):

        student = self.get_object(pk)

        if student is None:
            return Response(
                {
                    "detail": "Student not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        student.status = "inactive"
        student.profile.is_active = False
        student.profile.save(update_fields=["is_active"])

        student.save(
            update_fields=["status"]
        )

        return Response(
            {
                "detail": "Student deactivated successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
    