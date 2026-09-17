from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from .models import Notification, PushToken
from .serializers import NotificationSerializer, PushTokenSerializer


class NotificationPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class RegisterPushTokenView(APIView):
    """
    POST   /notifications/push-token/   { "token": "...", "platform": "ios" }
    DELETE /notifications/push-token/   { "token": "..." }   (call on logout)
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PushTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        platform = serializer.validated_data.get("platform", "")

        # A token belongs to one physical device; if it was previously
        # registered under a different account (e.g. shared device,
        # logout/login as someone else), move it rather than erroring.
        PushToken.objects.update_or_create(
            token=token,
            defaults={"user": request.user, "platform": platform},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"token": ["This field is required."]}, status=status.HTTP_400_BAD_REQUEST)
        PushToken.objects.filter(token=token, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class NotificationListView(ListAPIView):
    """GET /notifications/  -> paginated list, newest first, for the current user."""

    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)


class UnreadCountView(APIView):
    """GET /notifications/unread-count/ -> { "count": <int> }"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(recipient=request.user, read=False).count()
        return Response({"count": count})


class MarkNotificationReadView(APIView):
    """POST /notifications/{id}/mark-read/"""

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        updated = Notification.objects.filter(pk=pk, recipient=request.user).update(read=True)
        if not updated:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)


class MarkAllNotificationsReadView(APIView):
    """POST /notifications/mark-all-read/"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(recipient=request.user, read=False).update(read=True)
        return Response(status=status.HTTP_204_NO_CONTENT)
