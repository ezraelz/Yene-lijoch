from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Conversation, Message
from .permissions import IsConversationParticipant
from .serializers import ConversationSerializer, MessageSerializer
from .utils import role_for_user


class ConversationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET  /chat/conversations/                 -> role-scoped list
    GET  /chat/conversations/{id}/             -> retrieve
    GET  /chat/conversations/{id}/messages/    -> list messages
    POST /chat/conversations/{id}/messages/    -> send { "text": "..." }
    POST /chat/conversations/{id}/mark_read/   -> mark thread read for caller
    """

    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        user = self.request.user
        qs = Conversation.objects.select_related(
            "teacher__profile", "parent__profile", "student__profile"
        )
        teacher_profile = getattr(user, "teacher_profile", None)
        if teacher_profile is not None:
            return qs.filter(teacher=teacher_profile)

        parent_profile = getattr(user, "parent_profile", None)
        if parent_profile is not None:
            return qs.filter(parent=parent_profile)

        return qs.none()

    @action(detail=True, methods=["get", "post"])
    def messages(self, request, pk=None):
        conversation = self.get_object()  # enforces IsConversationParticipant

        if request.method == "GET":
            msgs = conversation.messages.select_related("sender").all()
            return Response(MessageSerializer(msgs, many=True).data)

        role = role_for_user(request.user)
        if role is None:
            return Response(
                {"detail": "User is neither a teacher nor a parent."},
                status=status.HTTP_403_FORBIDDEN,
            )

        text = (request.data.get("text") or "").strip()
        if not text:
            return Response({"detail": "text is required"}, status=status.HTTP_400_BAD_REQUEST)

        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            sender_role=role,
            text=text,
            read_by_teacher=role == "teacher",
            read_by_parent=role == "parent",
        )

        data = MessageSerializer(message).data
        self._broadcast(conversation.id, data)
        return Response(data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"])
    def mark_read(self, request, pk=None):
        conversation = self.get_object()
        role = request.data.get("role") or role_for_user(request.user)

        if role == "teacher":
            conversation.messages.exclude(sender_role="teacher").update(read_by_teacher=True)
        elif role == "parent":
            conversation.messages.exclude(sender_role="parent").update(read_by_parent=True)
        else:
            return Response({"detail": "role must be teacher or parent"}, status=400)

        return Response({"status": "ok"})

    def _broadcast(self, conversation_id, message_data):
        channel_layer = get_channel_layer()
        if channel_layer is None:
            return
        async_to_sync(channel_layer.group_send)(
            f"conversation_{conversation_id}",
            {"type": "chat.message", "message": message_data},
        )
