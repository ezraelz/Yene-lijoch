from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Lesson
from .serializers import (
    LessonSerializer,
    LessonCreateSerializer,
    LessonEditSerializer,
)


class LessonListCreateAPIView(APIView):
    """
    GET  /lessons/
        List all lessons.

    POST /lessons/
        Create a new lesson.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):

        lessons = (
            Lesson.objects
            .select_related(
                "course",
                "classroom",
                "teacher__profile",
            )
            .order_by(
                "-lesson_date",
                "-start_time"
            )
        )

        serializer = LessonSerializer(
            lessons,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = LessonCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            lesson = serializer.save()

            response_serializer = LessonSerializer(
                lesson
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class LessonDetailAPIView(APIView):
    """
    GET    /lessons/<id>/
    PUT    /lessons/<id>/
    PATCH  /lessons/<id>/
    DELETE /lessons/<id>/
    """

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAdminUser()]

    def get_object(self, pk):

        try:

            return (
                Lesson.objects
                .select_related(
                    "course",
                    "classroom",
                    "teacher__profile",
                )
                .get(pk=pk)
            )

        except Lesson.DoesNotExist:

            return None

    def get(self, request, pk):

        lesson = self.get_object(pk)

        if lesson is None:

            return Response(
                {
                    "detail": "Lesson not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LessonSerializer(
            lesson
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):

        lesson = self.get_object(pk)

        if lesson is None:

            return Response(
                {
                    "detail": "Lesson not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LessonEditSerializer(
            lesson,
            data=request.data
        )

        if serializer.is_valid():

            lesson = serializer.save()

            response_serializer = LessonSerializer(
                lesson
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

        lesson = self.get_object(pk)

        if lesson is None:

            return Response(
                {
                    "detail": "Lesson not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = LessonEditSerializer(
            lesson,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            lesson = serializer.save()

            response_serializer = LessonSerializer(
                lesson
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

        lesson = self.get_object(pk)

        if lesson is None:

            return Response(
                {
                    "detail": "Lesson not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        lesson.delete()

        return Response(
            {
                "detail": "Lesson deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
    