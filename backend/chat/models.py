from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Conversation(models.Model):
    """
    One thread between a specific Teacher and a specific Parent, about a
    specific Student. Uses the project's real models directly rather than
    inventing new ones.
    """

    teacher = models.ForeignKey(
        "teachers.Teacher", related_name="conversations", on_delete=models.CASCADE
    )
    parent = models.ForeignKey(
        "parents.Parent", related_name="conversations", on_delete=models.CASCADE
    )
    student = models.ForeignKey(
        "students.Student", related_name="conversations", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("teacher", "parent", "student")
        ordering = ["-created_at"]

    def clean(self):
        # Enforce the real relationship: this parent must actually be
        # linked to this student via Parent.student (M2M).
        if self.parent_id and self.student_id:
            if not self.parent.student.filter(pk=self.student_id).exists():
                raise ValidationError(
                    "This parent is not linked to this student."
                )

    def __str__(self):
        return f"{self.teacher} <-> {self.parent} re: {self.student}"


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation, related_name="messages", on_delete=models.CASCADE
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # users.Profile
        related_name="sent_chat_messages",
        on_delete=models.CASCADE,
    )
    sender_role = models.CharField(max_length=10)  # "teacher" | "parent", set at send time
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    read_by_teacher = models.BooleanField(default=False)
    read_by_parent = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"[{self.sender_role}] {self.text[:30]}"
