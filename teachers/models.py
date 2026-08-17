from django.db import models
from django.contrib.postgres.fields import ArrayField
from users.models import Profile
from courses.models import Course

class Teacher(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="teacher_profile")
    church = models.ForeignKey("churches.Church", on_delete=models.CASCADE)
    subject = models.ManyToManyField(Course, verbose_name="Subject", blank=True)
    employment_date = models.DateField("Employment Date", blank=True, null=True)
    available_days = models.JSONField(default=list, blank=True) 
    
    class Meta:
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ["id"]

    def __str__(self):
        subjects = ", ".join([subject.course_name for subject in self.subject.all()])  # ✅ Fixed M2M issue
        return f"{self.profile.first_name} {self.profile.last_name}"

    def save(self, *args, **kwargs):
        # Validate available_days
        valid_days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        if not isinstance(self.available_days, list):
            self.available_days = []
        invalid_days = [day for day in self.available_days if day not in valid_days]
        if invalid_days:
            raise ValueError(f"Invalid days in available_days: {invalid_days}")
        super().save(*args, **kwargs)