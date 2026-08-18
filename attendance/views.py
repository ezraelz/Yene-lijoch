from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Attendance
from .serializers import (
    AttendanceSerializer,
    AttendanceCreateSerializer,
    AttendanceEditSerializer,
)


class AttendanceListCreateAPIView(APIView):

    permission_classes = [IsAdminUser]

    def get(self, request):

        attendance = (
            Attendance.objects
            .select_related(
                "student__profile",
                "lesson__classroom",
            )
            .order_by(
                "lesson__lesson_date",
                "student__profile__first_name",
            )
        )

        serializer = AttendanceSerializer(
            attendance,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = AttendanceCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            attendance = serializer.save()

            response_serializer = AttendanceSerializer(
                attendance
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AttendanceDetailAPIView(APIView):

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAdminUser()]

    def get_object(self, pk):

        try:

            return (
                Attendance.objects
                .select_related(
                    "student__profile",
                    "lesson__classroom",
                )
                .get(pk=pk)
            )

        except Attendance.DoesNotExist:

            return None

    def get(self, request, pk):

        attendance = self.get_object(pk)

        if attendance is None:

            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AttendanceSerializer(
            attendance
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):

        attendance = self.get_object(pk)

        if attendance is None:

            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AttendanceEditSerializer(
            attendance,
            data=request.data
        )

        if serializer.is_valid():

            attendance = serializer.save()

            response_serializer = AttendanceSerializer(
                attendance
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

        attendance = self.get_object(pk)

        if attendance is None:

            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AttendanceEditSerializer(
            attendance,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            attendance = serializer.save()

            response_serializer = AttendanceSerializer(
                attendance
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

        attendance = self.get_object(pk)

        if attendance is None:

            return Response(
                {
                    "detail": "Attendance record not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        attendance.delete()

        return Response(
            {
                "detail": "Attendance deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )