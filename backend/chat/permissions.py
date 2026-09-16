from rest_framework.permissions import BasePermission


class IsConversationParticipant(BasePermission):
    """Only the teacher or parent on a conversation may read/write it."""

    def has_object_permission(self, request, view, obj):
        user = request.user
        teacher_profile = getattr(user, "teacher_profile", None)
        parent_profile = getattr(user, "parent_profile", None)
        return (
            (teacher_profile is not None and obj.teacher_id == teacher_profile.id)
            or (parent_profile is not None and obj.parent_id == parent_profile.id)
        )
