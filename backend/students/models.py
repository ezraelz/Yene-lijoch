from django.db import models

class Student(models.Model):
    profile = models.OneToOneField("users.Profile", on_delete=models.CASCADE, related_name="student_profile")
    organization = models.ForeignKey("organizations.Organization", on_delete=models.CASCADE)
    guardian_name = models.CharField(max_length=150, default="parent")
    guardian_contact = models.CharField(max_length=15, default="+251")
    status = models.CharField(max_length=50, choices=[("active", "Active"),("inactive", "Inactive"), ("graduated", "Graduated")], null=True, blank=True)
    enrollment_date = models.DateField(("Enrollment date"), auto_now=False, auto_now_add=False, blank=True, null=True)

    def __str__(self):
        return f"{self.profile.first_name} - {self.profile.last_name}"
    
