from django.db import models
from users.models import Profile
import uuid

class NotificationType(models.TextChoices):
    NEW_VIDEO_ADDED = "new_video_added"
    NEW_MESSAGE = "new_chat_message"
    NEW_STUDENT = "new_student_added"
    NEW_LESSON = "new_lesson"
    NEW_PARENT_JOINED = "new_parent_joined"
    CHAT = ("chat","Chat",)
    SYSTEM = ("system","System",)

class Notification(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE,related_name="notifications")
    title = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    data = models.JSONField(default=dict, blank=True)
    notification_type = models.CharField(max_length=20,choices=NotificationType.choices, default=NotificationType.SYSTEM,)
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=255,blank=True,)
    created_at = models.DateTimeField(auto_now_add=True,db_index=True,)
    read_at = models.DateTimeField(null=True,blank=True)

    class Meta:
        ordering = [ "-created_at",]
        indexes = [
            models.Index(fields=["user","-created_at",]),
            models.Index(fields=["user","is_read",]),
            models.Index(fields=["notification_type",]),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.title}"

    def to_payload(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "type": self.notification_type,
            "created_at": self.created_at.isoformat(),
            "is_read": self.is_read,
            "data": self.data,
        }
    