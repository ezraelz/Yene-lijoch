from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import ClassRoom
from .serializers import (
    ClassRoomSerializer,
    ClassRoomCreateSerializer,
    ClassRoomEditSerializer,
)


class ClassRoomListCreateAPIView(APIView):
    """
    GET  /classes/
        List all classes.

    POST /classes/
        Create a new class.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):

        classes = (
            ClassRoom.objects
            .select_related(
                "church",
                "teacher__profile",
                "course",
            )
            .prefetch_related(
                "students__profile"
            )
            .order_by("-created_at")
        )

        serializer = ClassRoomSerializer(
            classes,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = ClassRoomCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            classroom = serializer.save()

            response_serializer = ClassRoomSerializer(
                classroom
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ClassRoomDetailAPIView(APIView):
    """
    GET    /classes/<id>/
    PUT    /classes/<id>/
    PATCH  /classes/<id>/
    DELETE /classes/<id>/
    """

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAdminUser()]

    def get_object(self, pk):

        try:

            return (
                ClassRoom.objects
                .select_related(
                    "church",
                    "teacher__profile",
                    "course",
                )
                .prefetch_related(
                    "students__profile"
                )
                .get(pk=pk)
            )

        except ClassRoom.DoesNotExist:

            return None

    def get(self, request, pk):

        classroom = self.get_object(pk)

        if classroom is None:

            return Response(
                {
                    "detail": "Class not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClassRoomSerializer(
            classroom
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):

        classroom = self.get_object(pk)

        if classroom is None:

            return Response(
                {
                    "detail": "Class not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClassRoomEditSerializer(
            classroom,
            data=request.data
        )

        if serializer.is_valid():

            classroom = serializer.save()

            response_serializer = ClassRoomSerializer(
                classroom
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

        classroom = self.get_object(pk)

        if classroom is None:

            return Response(
                {
                    "detail": "Class not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ClassRoomEditSerializer(
            classroom,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            classroom = serializer.save()

            response_serializer = ClassRoomSerializer(
                classroom
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

        classroom = self.get_object(pk)

        if classroom is None:

            return Response(
                {
                    "detail": "Class not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        classroom.delete()

        return Response(
            {
                "detail": "Class deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )