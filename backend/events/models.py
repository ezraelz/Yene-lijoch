from django.db import models
from django.utils import timezone
from django.conf import settings


class Event(models.Model):

    # ------------------------------------------------------------------
    # Choices
    # ------------------------------------------------------------------
    EVENT_TYPES = [
        ("service", "Service"),
        ("bible_study", "Bible Study"),
        ("conference", "Conference"),
        ("meeting", "Meeting"),
        ("youth", "Youth"),
        ("children", "Children"),
        ("workshop", "Workshop"),
        ("other", "Other"),
    ]

    STATUS_UPCOMING = "upcoming"
    STATUS_ONGOING = "ongoing"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_UPCOMING, "Upcoming"),
        (STATUS_ONGOING, "Ongoing"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    AUDIENCE_DEFAULT = "Kids & Parents"
    LOCATION_DEFAULT = "Church"
    DESCRIPTION_DEFAULT = "Event published for parents by admin."

    # ------------------------------------------------------------------
    # Ownership (never sent by the client — set from request.user)
    # ------------------------------------------------------------------
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="events",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_events",
    )

    # ------------------------------------------------------------------
    # Core content
    # ------------------------------------------------------------------
    title = models.CharField(max_length=200)
    description = models.TextField(default=DESCRIPTION_DEFAULT, blank=True)

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        default="other",
    )

    location = models.CharField(
        max_length=255,
        default=LOCATION_DEFAULT,
        blank=True,
    )

    # Frontend: audience ("Kids & Parents")
    audience = models.CharField(
        max_length=150,
        default=AUDIENCE_DEFAULT,
        blank=True,
    )

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField(blank=True, null=True)

    # Optional human-readable labels the frontend already produces.
    # e.g. date_label="October 12, 2026", time_label="11:00 AM"
    date_label = models.CharField(max_length=60, blank=True)
    time_label = models.CharField(max_length=30, blank=True)

    # ------------------------------------------------------------------
    # Status / publishing
    # ------------------------------------------------------------------
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_UPCOMING,
        db_index=True,
    )

    published = models.BooleanField(
        default=True,
        help_text="When False the event is hidden from parents.",
    )

    # ------------------------------------------------------------------
    # Media
    # ------------------------------------------------------------------
    image = models.ImageField(upload_to="events/%Y/%m/", blank=True, null=True)

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_datetime"]
        verbose_name = "Event"
        verbose_name_plural = "Events"
        indexes = [
            models.Index(fields=["organization", "status", "published"]),
            models.Index(fields=["organization", "-start_datetime"]),
        ]

    def __str__(self):
        return self.title

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def display_date(self):
        if self.date_label:
            return self.date_label
        return timezone.localtime(self.start_datetime).strftime("%B %d, %Y")

    @property
    def display_time(self):
        if self.time_label:
            return self.time_label
        return timezone.localtime(self.start_datetime).strftime("%I:%M %p")

    def toggle_published(self):
        self.published = not self.published
        self.save(update_fields=["published", "updated_at"])
        return self.published
    