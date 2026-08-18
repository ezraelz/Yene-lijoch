from django.db import models
from users.models import Profile
from students.models import Student

class Parent(models.Model):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name="parent_profile")
    church = models.ForeignKey("churches.Church", on_delete=models.CASCADE)

    student = models.ManyToManyField(Student, related_name="parents")
    relationship = models.CharField(max_length=50, choices=[("father", "Father"), ("mother", "Mother"), ("guardian", "Guardian")])

    def __str__(self):
        student_names = ", ".join([f"{student.profile.first_name} {student.profile.last_name}" for student in self.student.all()])
        return f"{self.profile.first_name} - {self.profile.last_name} - ({self.relationship}) - {student_names}"
