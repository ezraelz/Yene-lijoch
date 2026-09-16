from rest_framework import serializers

from .models import Conversation, Message
from .utils import color_for, initials_for


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = [
            "id",
            "conversation",
            "sender",
            "sender_role",
            "text",
            "created_at",
            "read_by_teacher",
            "read_by_parent",
        ]
        read_only_fields = ["sender", "sender_role", "created_at"]


class ConversationSerializer(serializers.ModelSerializer):
    """
    Field names mirror what TeacherMessagesList.tsx reads off each `item`:
    parentName, childName, lastMessage, lastTime, unreadForTeacher,
    parentInitials, parentColor.
    """

    parentName = serializers.SerializerMethodField()
    childName = serializers.SerializerMethodField()
    teacherName = serializers.SerializerMethodField()
    lastMessage = serializers.SerializerMethodField()
    lastTime = serializers.SerializerMethodField()
    unreadForTeacher = serializers.SerializerMethodField()
    unreadForParent = serializers.SerializerMethodField()
    parentInitials = serializers.SerializerMethodField()
    parentColor = serializers.SerializerMethodField()
    teacherInitials = serializers.SerializerMethodField()
    teacherColor = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            "id",
            "parentName",
            "childName",
            "teacherName",
            "lastMessage",
            "lastTime",
            "unreadForTeacher",
            "unreadForParent",
            "parentInitials",
            "parentColor",
            "teacherInitials",
            "teacherColor",
        ]

    def get_parentName(self, obj):
        return obj.parent.profile.get_full_name()

    def get_childName(self, obj):
        return obj.student.full_name

    def get_teacherName(self, obj):
        return obj.teacher.profile.get_full_name()

    def get_parentInitials(self, obj):
        return initials_for(obj.parent.profile)

    def get_parentColor(self, obj):
        return color_for(obj.parent_id)

    def get_teacherInitials(self, obj):
        return initials_for(obj.teacher.profile)

    def get_teacherColor(self, obj):
        # Offset the palette index so a teacher and parent who happen to
        # share a numeric id don't land on the same color.
        return color_for(obj.teacher_id + 4)

    def _last_message(self, obj):
        return obj.messages.order_by("-created_at").first()

    def get_lastMessage(self, obj):
        m = self._last_message(obj)
        return m.text if m else ""

    def get_lastTime(self, obj):
        m = self._last_message(obj)
        return (m.created_at if m else obj.created_at).isoformat()

    def get_unreadForTeacher(self, obj):
        return obj.messages.filter(read_by_teacher=False).exclude(sender_role="teacher").count()

    def get_unreadForParent(self, obj):
        return obj.messages.filter(read_by_parent=False).exclude(sender_role="parent").count()
    