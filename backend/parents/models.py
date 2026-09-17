from django.db import models
from users.models import Profile
from students.models import Student

class Parent(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="parent_profile")
    student = models.ManyToManyField(Student, related_name="parents")
    relationship = models.CharField(max_length=50, choices=[("father", "Father"), ("mother", "Mother"), ("guardian", "Guardian")])

    def __str__(self):
        student_names = ", ".join([f"{student.profile.first_name} {student.profile.last_name}" for student in self.student.all()])
        return f"{self.profile.first_name} - {self.profile.last_name} - ({self.relationship}) - {student_names}"

    @property
    def full_name(self):
        """Prefer the linked Profile; fall back to the guardian name."""
        profile = self.profile
        if profile:
            return profile.get_full_name()
        return self.guardian_name or ""
    