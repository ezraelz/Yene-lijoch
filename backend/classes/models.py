from django.db import models


class ClassRoom(models.Model):

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("completed", "Completed"),
    ]

    church = models.ForeignKey( "churches.Church", on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=200)
    age_group = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    teacher = models.ForeignKey("teachers.Teacher",on_delete=models.SET_NULL,null=True,blank=True, related_name="classes")
    students = models.ManyToManyField( "students.Student", blank=True, related_name="classes")
    room = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"

    def __str__(self):
        return self.name
    