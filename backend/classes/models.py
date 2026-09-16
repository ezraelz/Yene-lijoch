from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.conf import settings


class ClassRoom(models.Model):
    """
    A Sunday school 'Group' shown on the AdminGroupsScreen.

    Frontend shape (from `addGroup(groupName, teacherName)`):
        { id, name, teacherName, students: [...] }

    Also keeps the richer scheduling / lifecycle fields used elsewhere
    in the app (lessons, events, etc.).
    """

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_COMPLETED, "Completed"),
    ]

    # ------------------------------------------------------------------
    # Ownership
    # ------------------------------------------------------------------
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="classes",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_classes",
    )

    # ------------------------------------------------------------------
    # Core identity
    # ------------------------------------------------------------------
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    # Frontend renders `group.teacherName` as a plain string.
    # Keep the FK for relational queries, plus a denormalised name for
    # the UI fallback when the FK is null (as the frontend does).
    teacher = models.ForeignKey(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="classes",
    )
    teacher_name = models.CharField(
        max_length=200,
        blank=True,
        default="",
        help_text=(
            "Display-only teacher name. Used when no Teacher FK is set, "
            "mirroring the frontend's free-text 'teacherName' field."
        ),
    )

    # ------------------------------------------------------------------
    # Age group / demographics
    # ------------------------------------------------------------------
    age_group = models.CharField(max_length=50, null=True, blank=True)
    grade = models.CharField(
        max_length=50,
        blank=True,
        default="",
        help_text='Primary grade for this group, e.g. "Grade 3".',
    )

    # ------------------------------------------------------------------
    # Students (M2M kept, but the UI's source of truth is the reverse FK
    # on Student.classroom — see Student model below).
    # ------------------------------------------------------------------
    students = models.ManyToManyField(
        "students.Student",
        blank=True,
        related_name="classes",
    )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        db_index=True,
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        indexes = [
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["organization", "name"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "name"],
                name="unique_class_name_per_organization",
            ),
        ]

    def __str__(self):
        return self.name

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def display_teacher_name(self):
        """
        Match the frontend's `group.teacherName`:
        prefer the FK's full name, fall back to the free-text field.
        """
        if self.teacher_id and getattr(self.teacher, "profile", None):
            profile = self.teacher.profile
            full = f"{profile.first_name} {profile.last_name}".strip()
            if full:
                return full
        return self.teacher_name or ""

    @property
    def student_count(self):
        return self.students.count()

    @property
    def slug(self):
        return slugify(self.name)
    