from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Q
from django.utils import timezone
from .models import Announcement
from .serializers import AnnouncementSerializer


class AnnouncementListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        announcements = Announcement.objects.select_related(
            "church",
            "created_by"
        )

        if hasattr(request.user, "profile"):
            church = request.user.profile.church

            if church:
                announcements = announcements.filter(
                    church=church
                )

        audience = request.query_params.get("audience")

        if audience:
            announcements = announcements.filter(
                audience__in=[
                    Announcement.Audience.ALL,
                    audience.upper()
                ]
            )

        published = request.query_params.get("published")

        if published != "false":

            now = timezone.now()

            announcements = announcements.filter(
                is_published=True
            ).filter(
                Q(publish_at__isnull=True) |
                Q(publish_at__lte=now)
            ).filter(
                Q(expires_at__isnull=True) |
                Q(expires_at__gt=now)
            )

        serializer = AnnouncementSerializer(
            announcements,
            many=True
        )

        return Response(serializer.data)
    def post(self, request):

        serializer = AnnouncementSerializer(
            data=request.data
        )

        if serializer.is_valid():

            church = None

            if hasattr(request.user, "profile"):
                church = request.user.profile.church

            if not church:
                return Response(
                    {
                        "detail": "Your account is not associated with a church."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            announcement = serializer.save(
                church=church,
                created_by=request.user
            )

            return Response(
                AnnouncementSerializer(announcement).data,
                status=status.HTTP_201_CREATED
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class AnnouncementDetailAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):

        try:
            announcement = Announcement.objects.select_related(
                "church",
                "created_by"
            ).get(pk=pk)
        except Announcement.DoesNotExist:
            return None

        # Make sure user can only access announcements
        # from their church
        if hasattr(request.user, "profile"):

            user_church = request.user.profile.church

            if announcement.church != user_church:
                return None

        return announcement

    def get(self, request, pk):

        announcement = self.get_object(request, pk)

        if not announcement:
            return Response(
                {"detail": "Announcement not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AnnouncementSerializer(announcement)

        return Response(serializer.data)

    def put(self, request, pk):

        announcement = self.get_object(request, pk)

        if not announcement:
            return Response(
                {"detail": "Announcement not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AnnouncementSerializer(
            announcement,
            data=request.data
        )

        if serializer.is_valid():

            announcement = serializer.save()

            return Response(
                AnnouncementSerializer(announcement).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, pk):

        announcement = self.get_object(request, pk)

        if not announcement:
            return Response(
                {"detail": "Announcement not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AnnouncementSerializer(
            announcement,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():

            announcement = serializer.save()

            return Response(
                AnnouncementSerializer(announcement).data
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):

        announcement = self.get_object(request, pk)

        if not announcement:
            return Response(
                {"detail": "Announcement not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        announcement.delete()

        return Response(
            {"detail": "Announcement deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )