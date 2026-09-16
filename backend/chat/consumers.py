from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Conversation


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """
    Connect at:
        ws://<host>/ws/chat/<conversation_id>/?token=<jwt access token>
    """

    async def connect(self):
        self.conversation_id = self.scope["url_route"]["kwargs"]["conversation_id"]
        self.group_name = f"conversation_{self.conversation_id}"

        user = self.scope["user"]
        if not user or not user.is_authenticated:
            await self.close(code=4401)
            return

        allowed = await self._user_is_participant(user, self.conversation_id)
        if not allowed:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # Invoked by ConversationViewSet._broadcast via channel_layer.group_send
    async def chat_message(self, event):
        await self.send_json(event["message"])

    @staticmethod
    @database_sync_to_async
    def _user_is_participant(user, conversation_id):
        try:
            convo = Conversation.objects.select_related("teacher", "parent").get(
                id=conversation_id
            )
        except Conversation.DoesNotExist:
            return False

        teacher_profile = getattr(user, "teacher_profile", None)
        parent_profile = getattr(user, "parent_profile", None)
        return (
            (teacher_profile is not None and convo.teacher_id == teacher_profile.id)
            or (parent_profile is not None and convo.parent_id == parent_profile.id)
        )
