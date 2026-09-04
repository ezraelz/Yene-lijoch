from django.db import models
from django.conf import settings

from organizations.models import Organization


class Announcement(models.Model):

    class Audience(models.TextChoices):
        ALL = "ALL", "Everyone"
        TEACHERS = "TEACHERS", "Teachers"
        PARENTS = "PARENTS", "Parents"
        STUDENTS = "STUDENTS", "Students"

    class Priority(models.TextChoices):
        NORMAL = "NORMAL", "Normal"
        IMPORTANT = "IMPORTANT", "Important"
        URGENT = "URGENT", "Urgent"

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=255)
    content = models.TextField()
    audience = models.CharField(max_length=20,choices=Audience.choices,default=Audience.ALL)
    priority = models.CharField( max_length=20, choices=Priority.choices,default=Priority.NORMAL)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL, null=True, blank=True, related_name="created_announcements")
    is_published = models.BooleanField(default=True)
    publish_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title
    