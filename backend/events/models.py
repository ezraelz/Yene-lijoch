from django.db import models

class Event(models.Model):

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

    STATUS_CHOICES = [
        ("upcoming", "Upcoming"),
        ("ongoing", "Ongoing"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    church = models.ForeignKey(
        "churches.Church",
        on_delete=models.CASCADE,
        related_name="events"
    )

    title = models.CharField(
        max_length=200
    )

    description = models.TextField(
        blank=True
    )

    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPES,
        default="other"
    )

    location = models.CharField(
        max_length=255,
        blank=True
    )

    start_datetime = models.DateTimeField()

    end_datetime = models.DateTimeField(
        blank=True,
        null=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="upcoming"
    )

    image = models.ImageField(
        upload_to="events/",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-start_datetime"]
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title
    