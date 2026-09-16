from django.db import models


class Attendance(models.Model):

    STATUS_PRESENT = "present"
    STATUS_ABSENT = "absent"
    STATUS_LATE = "late"
    STATUS_EXCUSED = "excused"
    STATUS_CHOICES = [
        (STATUS_PRESENT, "Present"),
        (STATUS_ABSENT, "Absent"),
        (STATUS_LATE, "Late"),
        (STATUS_EXCUSED, "Excused"),
    ]

    lesson = models.ForeignKey(
        "lessons.Lesson",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    student = models.ForeignKey(
        "students.Student",
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PRESENT,
        db_index=True,
    )

    note = models.TextField(blank=True)

    # Who recorded it (nullable so deleting a teacher doesn't lose history).
    recorded_by = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_recorded",
    )

    recorded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["student__profile__first_name"]
        constraints = [
            models.UniqueConstraint(
                fields=["lesson", "student"],
                name="unique_student_lesson_attendance",
            )
        ]
        indexes = [
            models.Index(fields=["lesson", "status"]),
            models.Index(fields=["student", "-recorded_at"]),
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
    