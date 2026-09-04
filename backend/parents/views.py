from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from .models import Parent
from .serializers import (
    ParentSerializer,
    ParentEditSerializer,
    ParentRegisterSerializer,
)


class ParentListCreateAPIView(APIView):
    """
    GET  /parents/
        List all parents.

    POST /parents/
        Register a new parent.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):

        parents = (
            Parent.objects
            .select_related(
                "profile",
                "organization"
            )
            .prefetch_related(
                "student__profile"
            )
            .order_by("id")
        )

        serializer = ParentSerializer(
            parents,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):

        serializer = ParentRegisterSerializer(
            data=request.data
        )

        if serializer.is_valid():

            profile = serializer.save()

            # Get newly created Parent
            parent = profile.parent_profile

            response_serializer = ParentSerializer(
                parent
            )

            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ParentDetailAPIView(APIView):
    """
    GET    /parents/<id>/
    PUT    /parents/<id>/
    PATCH  /parents/<id>/
    DELETE /parents/<id>/
    """

    def get_permissions(self):

        if self.request.method == "GET":
            return [IsAuthenticated()]

        return [IsAdminUser()]

    def get_object(self, pk):

        try:
            return (
                Parent.objects
                .select_related(
                    "profile",
                    "organization"
                )
                .prefetch_related(
                    "student__profile"
                )
                .get(pk=pk)
            )

        except Parent.DoesNotExist:
            return None

    def get(self, request, pk):

        parent = self.get_object(pk)

        if parent is None:
            return Response(
                {
                    "detail": "Parent not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ParentSerializer(
            parent
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):

        parent = self.get_object(pk)

        if parent is None:
            return Response(
                {
                    "detail": "Parent not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ParentEditSerializer(
            parent,
            data=request.data
        )

        if serializer.is_valid():

            parent = serializer.save()

            response_serializer = ParentSerializer(
                parent
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

        parent = self.get_object(pk)

        if parent is None:
            return Response(
                {
                    "detail": "Parent not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ParentEditSerializer(
            parent,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            parent = serializer.save()

            response_serializer = ParentSerializer(
                parent
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

        parent = self.get_object(pk)

        if parent is None:
            return Response(
                {
                    "detail": "Parent not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        parent.delete()

        return Response(
            {
                "detail": "Parent deleted successfully."
            },
            status=status.HTTP_204_NO_CONTENT
        )

    