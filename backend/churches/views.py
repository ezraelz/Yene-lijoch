from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from .models import Church
from .serializers import ChurchSerializer


class ChurchListCreateAPIView(APIView):
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        churches = Church.objects.all().order_by('-created_at')
        serializer = ChurchSerializer(churches, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = ChurchSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class ChurchDetailAPIView(APIView):

    def get_object(self, pk):
        try:
            return Church.objects.get(pk=pk)
        except Church.DoesNotExist:
            return None

    def get(self, request, pk):
        church = self.get_object(pk)

        if church is None:
            return Response(
                {"detail": "Church not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChurchSerializer(church)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        church = self.get_object(pk)

        if church is None:
            return Response(
                {"detail": "Church not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChurchSerializer(
            church,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):
        church = self.get_object(pk)

        if church is None:
            return Response(
                {"detail": "Church not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ChurchSerializer(
            church,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        church = self.get_object(pk)

        if church is None:
            return Response(
                {"detail": "Church not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        church.delete()

        return Response(
            {"detail": "Church deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    