from django.db import models


class Lesson(models.Model):

    STATUS_CHOICES = [
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    classroom = models.ForeignKey("classes.ClassRoom", on_delete=models.CASCADE, related_name="lessons")
    teacher = models.ForeignKey("teachers.Teacher", on_delete=models.SET_NULL, related_name="lessons", null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson_date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField( null=True,
        blank=True
    )

    content = models.TextField(
        blank=True
    )

    objectives = models.TextField(
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="planned"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-lesson_date", "-start_time"]
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"

    def __str__(self):
        return self.title