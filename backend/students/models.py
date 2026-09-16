from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver


class Student(models.Model):
    """
    A student enrolled in a Sunday school group.

    Bridges two things:
      1. The existing `Profile` model (identity: name, age, sex, etc.)
      2. The frontend's `addStudent({...})` payload:
            { name, groupId, grade, age, parentName, parentEmail }
    """

    # ------------------------------------------------------------------
    # Identity — always linked to a Profile
    # ------------------------------------------------------------------
    profile = models.OneToOneField(
        "users.Profile",
        on_delete=models.CASCADE,
        related_name="student_profile",
    )

    # ------------------------------------------------------------------
    # Ownership — matches the org-scoping used by every other model
    # ------------------------------------------------------------------
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="students",
        null=True,
        blank=True,
    )

    # The group this student belongs to (frontend's `groupId`).
    classroom = models.ForeignKey(
        "classes.ClassRoom",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="roster",
    )

    # ------------------------------------------------------------------
    # Academics — frontend: grade, age
    # ------------------------------------------------------------------
    grade = models.CharField(
        max_length=50,
        blank=True,
        default="Grade 1",
    )
    # `age` also lives on Profile; kept here as a convenience for the
    # admin list view. Kept in sync via `save()`.
    age = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(100)],
    )

    # ------------------------------------------------------------------
    # Guardian — frontend: parentName, parentEmail
    # ------------------------------------------------------------------
    guardian_name = models.CharField(
        max_length=150,
        default="Parent",
        blank=True,
        help_text="Frontend's `parentName`.",
    )
    guardian_email = models.EmailField(
        blank=True,
        default="parent@test.com",
        help_text="Frontend's `parentEmail`.",
    )
    guardian_contact = models.CharField(
        max_length=30,
        default="+251",
        blank=True,
        help_text="Existing field — kept for backward compatibility.",
    )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    STATUS_GRADUATED = "graduated"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_INACTIVE, "Inactive"),
        (STATUS_GRADUATED, "Graduated"),
    ]
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
        null=True,
        blank=True,
        db_index=True,
    )
    enrollment_date = models.DateField(
        null=True,
        blank=True,
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["profile__first_name", "profile__last_name"]
        verbose_name = "Student"
        verbose_name_plural = "Students"
        indexes = [
            models.Index(fields=["organization", "classroom"]),
            models.Index(fields=["organization", "status"]),
            models.Index(fields=["classroom", "status"]),
        ]

    def __str__(self):
        name = self.full_name
        return name or f"Student #{self.pk}"

    # ------------------------------------------------------------------
    # Read-only helpers
    # ------------------------------------------------------------------
    @property
    def full_name(self):
        """Prefer the linked Profile; fall back to the guardian name."""
        profile = self.profile
        if profile:
            return profile.get_full_name()
        return self.guardian_name or ""

    @property
    def parent_name(self):
        return self.guardian_name

    @property
    def parent_email(self):
        return self.guardian_email

    @property
    def group_name(self):
        return self.classroom.name if self.classroom_id else ""

    # ------------------------------------------------------------------
    # Keep `age` in sync with Profile.age
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        # If the caller set age on the Profile, prefer that.
        if self.profile_id and self.profile.age and self.age != self.profile.age:
            self.age = self.profile.age

        # If the caller set age on the Student, push it to the Profile.
        elif self.age and self.profile_id and not self.profile.age:
            self.profile.age = self.age
            self.profile.save(update_fields=["age"])

        # Derive organization from the classroom when missing.
        if not self.organization_id and self.classroom_id:
            self.organization = self.classroom.organization

        super().save(*args, **kwargs)

