from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.text import slugify


class Lesson(models.Model):
    """
    Curriculum lesson for Sunday school.

    Mirrors the SharedCurriculum shape used by the React Native admin app:
        { id, title, category, week, date, year, scripture,
          memoryVerse, description, status, published,
          coverUri, attachmentUri, attachmentName, attachmentType }
    """

    # ------------------------------------------------------------------
    # Status choices (frontend: "this_week" | "upcoming" | "completed")
    # ------------------------------------------------------------------
    STATUS_THIS_WEEK = "this_week"
    STATUS_UPCOMING = "upcoming"
    STATUS_COMPLETED = "completed"
    STATUS_CHOICES = [
        (STATUS_THIS_WEEK, "This Week"),
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_COMPLETED, "Completed"),
    ]

    # ------------------------------------------------------------------
    # Attachment kind choices (frontend: PickedFile.kind)
    # ------------------------------------------------------------------
    ATTACHMENT_IMAGE = "image"
    ATTACHMENT_VIDEO = "video"
    ATTACHMENT_AUDIO = "audio"  # frontend calls this "music"
    ATTACHMENT_DOCUMENT = "document"
    ATTACHMENT_KIND_CHOICES = [
        (ATTACHMENT_IMAGE, "Image"),
        (ATTACHMENT_VIDEO, "Video"),
        (ATTACHMENT_AUDIO, "Audio"),
        (ATTACHMENT_DOCUMENT, "Document"),
    ]

    CATEGORY_DEFAULT = "General"
    SCRIPTURE_DEFAULT = "Scripture TBA"
    MEMORY_VERSE_DEFAULT = "Memory verse TBA"
    DESCRIPTION_DEFAULT = "Sunday school curriculum lesson for parents."

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    classroom = models.ForeignKey(
        "classes.ClassRoom",
        on_delete=models.CASCADE,
        related_name="lessons",
        null=True,
        blank=True,
    )
    # ------------------------------------------------------------------
    # Core content
    # ------------------------------------------------------------------
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=100, default=CATEGORY_DEFAULT)
    week = models.PositiveSmallIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(53)],
        help_text="Week number within the year plan (1–53).",
    )

    # Frontend sends a human-readable date label ("September 21, 2026")
    # plus a separate year. We store the real date and derive the year.
    lesson_date = models.DateField(default=timezone.localdate)
    year = models.PositiveSmallIntegerField(
        default=timezone.now().year,
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
    )
    date_label = models.CharField(
        max_length=60,
        blank=True,
        help_text="Optional human-readable date label shown to parents.",
    )

    # ------------------------------------------------------------------
    # Lesson body
    # ------------------------------------------------------------------
    scripture = models.CharField(max_length=200, default=SCRIPTURE_DEFAULT)
    memory_verse = models.TextField(default=MEMORY_VERSE_DEFAULT, blank=True)
    description = models.TextField(default=DESCRIPTION_DEFAULT, blank=True)

    # ------------------------------------------------------------------
    # Status & publishing
    # ------------------------------------------------------------------
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_UPCOMING,
        db_index=True,
    )
    published = models.BooleanField(
        default=True,
        help_text="When False the lesson is hidden from parents.",
    )

    # ------------------------------------------------------------------
    # Media / attachments (frontend: coverUri, attachmentUri, ...)
    # ------------------------------------------------------------------
    cover = models.ImageField(
        upload_to="curriculum/covers/%Y/%m/",
        null=True,
        blank=True,
    )
    attachment = models.FileField(
        upload_to="curriculum/attachments/%Y/%m/",
        null=True,
        blank=True,
    )
    attachment_name = models.CharField(max_length=255, blank=True)
    attachment_type = models.CharField(
        max_length=20,
        choices=ATTACHMENT_KIND_CHOICES,
        blank=True,
    )

    objective = models.TextField(blank=True, default="")
    materials = models.JSONField(blank=True, default=list)   # list of {id, title, url?}
    activity = models.TextField(blank=True, default="")
    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-lesson_date", "-created_at"]
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        indexes = [
            models.Index(fields=["status", "published"]),
            models.Index(fields=["year", "week"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "year", "week"],
                name="unique_lesson_per_classroom_week",
            ),
        ]

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def __str__(self):
        return f"Week {self.week} · {self.title}"

    def save(self, *args, **kwargs):
        # Keep `year` in sync with `lesson_date`.
        if self.lesson_date:
            self.year = self.lesson_date.year
        # Normalise blank defaults.
        self.category = (self.category or "").strip() or self.CATEGORY_DEFAULT
        self.scripture = (self.scripture or "").strip() or self.SCRIPTURE_DEFAULT
        self.memory_verse = (self.memory_verse or "").strip() or self.MEMORY_VERSE_DEFAULT
        self.description = (self.description or "").strip() or self.DESCRIPTION_DEFAULT
        super().save(*args, **kwargs)

    def mark_this_week(self):
        """Frontend action: 'Make this week'."""
        type(self).objects.filter(status=self.STATUS_THIS_WEEK).exclude(pk=self.pk).update(
            status=self.STATUS_UPCOMING
        )
        self.status = self.STATUS_THIS_WEEK
        self.save(update_fields=["status", "updated_at"])

    def toggle_published(self):
        self.published = not self.published
        self.save(update_fields=["published", "updated_at"])
        return self.published

    @property
    def display_date(self):
        return self.date_label or self.lesson_date.strftime("%B %d, %Y")

    @property
    def slug(self):
        return slugify(f"week-{self.week}-{self.title}")