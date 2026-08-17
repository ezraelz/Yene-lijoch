from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Role
from .serializers import RoleSerializer
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser

class RoleView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        role = Role.objects.all()

        serializer = RoleSerializer(role, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = RoleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class RoleDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        role = Role.objects.get(id=pk)

        serializer = RoleSerializer(role)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def delete(self, request, pk):
        role = Role.objects.get(id=pk)
        role.delete()
        return Response({'Role has been deleted successfully!'})
    