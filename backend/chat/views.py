from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Conversation, Message
from .permissions import IsConversationParticipant
from .serializers import ConversationSerializer, MessageSerializer
from .utils import role_for_user
from notifications.services import notify_user


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

    # ------------------------------------------------------------------
    # create-or-get a conversation with a student's parent
    # ------------------------------------------------------------------
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        POST /chat/conversations/
        Body: { "student": <student_id> }

        - Teachers: creates (or returns existing) conversation with the
          student's parent.
        - Parents: creates (or returns existing) conversation with the
          student's teacher.

        Either role must supply the `student` they want to talk about;
        each role is scoped to only its own students (a teacher's own
        class, or a parent's own child).
        """
        user = request.user
        teacher_profile = getattr(user, "teacher_profile", None)
        parent_profile = getattr(user, "parent_profile", None)

        if teacher_profile is None and parent_profile is None:
            return Response(
                {"detail": "You must be a teacher or a parent to start a conversation."},
                status=status.HTTP_403_FORBIDDEN,
            )

        student_id = request.data.get("student")
        if not student_id:
            return Response(
                {"student": ["This field is required."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Import lazily to avoid circular imports at module load.
        from students.models import Student
        student = get_object_or_404(Student, pk=student_id)

        if teacher_profile is not None:
            # Scope check: the teacher must own the student's classroom.
            classroom = getattr(student, "classroom", None)
            if classroom and classroom.teacher_id != teacher_profile.id:
                return Response(
                    {
                        "detail": (
                            "You can only message parents of students "
                            "in your own classes."
                        )
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Find the parent for this student. Adjust the lookup to match
            # your `Parent` model's relationship to `Student`.
            parent = self._find_parent_for_student(student)
            if parent is None:
                return Response(
                    {"detail": "This student has no linked parent account."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            # Scope check: the caller must actually be one of this
            # student's linked parents (Parent.student is M2M, so a
            # student can have more than one — check membership, not
            # equality against a single fetched parent).
            if not student.parents.filter(pk=parent_profile.pk).exists():
                return Response(
                    {"detail": "You can only message teachers of your own children."},
                    status=status.HTTP_403_FORBIDDEN,
                )
            parent = parent_profile

            # Find the teacher for this student. Adjust the lookup to match
            # your `Student` -> classroom -> teacher relationship.
            teacher_profile = self._find_teacher_for_student(student)
            if teacher_profile is None:
                return Response(
                    {"detail": "This student has no assigned teacher."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        conversation, created = Conversation.objects.get_or_create(
            teacher=teacher_profile,
            parent=parent,
            student=student,
        )

        serializer = self.get_serializer(conversation)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )

    # ------------------------------------------------------------------
    def _find_parent_for_student(self, student):
        """
        Return *a* Parent profile for a given Student, or None.

        `Parent.student` is a ManyToManyField(Student, related_name="parents"),
        so a student can have more than one linked Parent (father, mother,
        guardian). This picks one arbitrarily via `.first()` — fine for the
        teacher-initiates-conversation flow, where any linked parent will do.
        Do NOT use this for permission checks on the parent side; use
        `student.parents.filter(pk=parent_profile.pk).exists()` instead,
        since equality against a single `.first()` result can wrongly deny
        a student's second/third parent.
        """
        return student.parents.first()

    def _find_teacher_for_student(self, student):
        """
        Return the Teacher profile for a given Student, or None.

        The version below assumes `Student.classroom.teacher` exists.
        Change it if your model differs (e.g. a direct `student.teacher`
        FK, or a many-teacher setup where you'd need to disambiguate).
        """
        classroom = getattr(student, "classroom", None)
        if classroom is not None:
            return getattr(classroom, "teacher", None)

        return None

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

    def _notify_new_message(self, conversation, message, sender_role):
        """Notify whichever side did NOT send the message."""
        if sender_role == "teacher":
            recipient_user = conversation.parent.profile.user
        else:
            recipient_user = conversation.teacher.profile.user

        notify_user(
            recipient=recipient_user,
            notification_type="new_message",
            title="New message",
            body=message.text[:140],
            data={"conversation_id": conversation.id, "screen": "chat"},
            actor=message.sender,
        )
        