from django.db import models
from django.contrib.postgres.fields import ArrayField
from users.models import Profile

class Teacher(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="teacher_profile")
    church = models.ForeignKey("churches.Church", on_delete=models.CASCADE)
    employment_date = models.DateField("Employment Date", blank=True, null=True)
    
    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ["id"]

    def __str__(self):
        return f"{self.profile.first_name} {self.profile.last_name}"
