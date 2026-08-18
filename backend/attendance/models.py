from django.db import models


class Attendance(models.Model):

    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("late", "Late"),
        ("excused", "Excused"),
    ]

    lesson = models.ForeignKey(
        "lessons.Lesson",
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="attendance_records"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="present"
    )

    note = models.TextField(
        blank=True
    )

    recorded_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["student__profile__first_name"]

        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "student"],
                name="unique_student_lesson_attendance"
            )
        ]

        verbose_name = "Attendance"
        verbose_name_plural = "Attendance Records"

    def __str__(self):
        return (
            f"{self.student.profile.first_name} "
            f"{self.student.profile.last_name} - "
            f"{self.lesson.title} - "
            f"{self.status}"
        )