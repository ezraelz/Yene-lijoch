# Not a real app file -- shows the exact diff to make in your existing
# chat/views.py so new messages trigger a notification to the other
# participant. Drop these lines into ConversationViewSet.messages().

from notifications.services import notify_user


# Inside ConversationViewSet.messages(), right after:
#
#   message = Message.objects.create(...)
#   data = MessageSerializer(message).data
#   self._broadcast(conversation.id, data)
#
# add:

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

# Then the call site becomes:
#
#   message = Message.objects.create(...)
#   data = MessageSerializer(message).data
#   self._broadcast(conversation.id, data)
#   self._notify_new_message(conversation, message, role)
#   return Response(data, status=status.HTTP_201_CREATED)
#
# NOTE: `conversation.parent.profile.user` / `conversation.teacher.profile.user`
# assumes Parent/Teacher each have a `profile` OneToOneField to `users.Profile`,
# and Profile has a `user` FK to the auth user (matching the Parent model you
# shared: `profile = OneToOneField(Profile, related_name="parent_profile")`).
# Adjust the attribute chain if your Profile -> User link is named differently.
