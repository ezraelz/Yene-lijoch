from django.contrib import admin

from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ("id", "teacher", "parent", "student", "created_at")
    list_select_related = ("teacher__profile", "parent__profile", "student__profile")


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("id", "conversation", "sender", "sender_role", "created_at")
    list_select_related = ("conversation", "sender")
