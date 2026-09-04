from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Event
from .serializers import (
    EventSerializer,
    EventCreateSerializer,
    EventEditSerializer,
)


class EventListCreateAPIView(APIView):
    """
    GET  /events/
        List all events.

    POST /events/
        Create a new event.
    """

    permission_classes = [IsAdminUser]

    def get(self, request):

        events = (
            Event.objects
            .select_related("organization")
            .order_by("-start_date")
        )

        serializer = EventSerializer(
            events,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = EventCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            event = serializer.save()

            response_serializer = EventSerializer(
                event
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class EventDetailAPIView(APIView):
    """
    GET    /events/<id>/
    PUT    /events/<id>/
    PATCH  /events/<id>/
    DELETE /events/<id>/
    """

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAdminUser()]

    def get_object(self, pk):

        try:
            return (
                Event.objects
                .select_related("organization")
                .get(pk=pk)
            )

        except Event.DoesNotExist:
            return None

    def get(self, request, pk):

        event = self.get_object(pk)

        if event is None:
            return Response(
                {
                    "detail": "Event not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EventSerializer(
            event
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):

        event = self.get_object(pk)

        if event is None:
            return Response(
                {
                    "detail": "Event not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EventEditSerializer(
            event,
            data=request.data
        )

        if serializer.is_valid():

            event = serializer.save()

            response_serializer = EventSerializer(
                event
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

        event = self.get_object(pk)

        if event is None:
            return Response(
                {
                    "detail": "Event not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EventEditSerializer(
            event,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            event = serializer.save()

            response_serializer = EventSerializer(
                event
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

        event = self.get_object(pk)

        if event is None:
            return Response(
                {
                    "detail": "Event not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        event.delete()

        return Response(
            {
                "detail": "Event deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )
    