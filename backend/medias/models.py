from django.db import models
from django.utils import timezone
from django.utils.text import slugify


class MediaItem(models.Model):
    """
    A single piece of media published to parents.

    Mirrors the frontend `addMedia({...})` payload from
    AdminVideosScreen.js:

        { title, kind, youtubeId, duration, ageGroup, description,
          published, source, localUri, coverUri, fileName, mimeType }
    """

    # ------------------------------------------------------------------
    # Choices
    # ------------------------------------------------------------------
    KIND_VIDEO = "video"
    KIND_SONG = "song"
    KIND_BIBLE_STORY = "bible_story"
    KIND_COURSE = "course"
    KIND_PICTURE = "picture"
    KIND_CHOICES = [
        (KIND_VIDEO, "Video"),
        (KIND_SONG, "Song"),
        (KIND_BIBLE_STORY, "Bible Story"),
        (KIND_COURSE, "Course"),
        (KIND_PICTURE, "Picture"),
    ]

    SOURCE_YOUTUBE = "youtube"
    SOURCE_GALLERY = "gallery"
    SOURCE_CHOICES = [
        (SOURCE_YOUTUBE, "YouTube"),
        (SOURCE_GALLERY, "Gallery"),
    ]

    # ------------------------------------------------------------------
    # Ownership (never sent by the client — set from request.user)
    # ------------------------------------------------------------------
    organization = models.ForeignKey(
        "organizations.Organization",
        on_delete=models.CASCADE,
        related_name="media_items",
    )
    created_by = models.ForeignKey(
        "users.Profile",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_media",
    )

    # ------------------------------------------------------------------
    # Core content
    # ------------------------------------------------------------------
    title = models.CharField(max_length=200)
    kind = models.CharField(
        max_length=20,
        choices=KIND_CHOICES,
        default=KIND_VIDEO,
        db_index=True,
    )
    description = models.TextField(blank=True)
    age_group = models.CharField(
        max_length=50,
        default="All ages",
        help_text='e.g. "Ages 5–10", "All ages".',
    )
    duration = models.CharField(
        max_length=20,
        default="3:00",
        help_text='Display string, e.g. "4:20" or "Gallery".',
    )

    # ------------------------------------------------------------------
    # Source / origin
    # ------------------------------------------------------------------
    source = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        default=SOURCE_GALLERY,
        db_index=True,
    )
    youtube_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Extracted YouTube video ID (not the full URL).",
    )

    # ------------------------------------------------------------------
    # Files
    # ------------------------------------------------------------------
    # The main media file (video / audio / image) uploaded from the gallery.
    file = models.FileField(
        upload_to="media/items/%Y/%m/",
        blank=True,
        null=True,
    )
    # Optional cover image (thumbnail shown in lists).
    cover = models.ImageField(
        upload_to="media/covers/%Y/%m/",
        blank=True,
        null=True,
    )
    # Original file name as sent by the client ("noahs_ark.mp4").
    file_name = models.CharField(max_length=255, blank=True)
    # MIME type ("video/mp4", "audio/mpeg", ...).
    mime_type = models.CharField(max_length=100, blank=True)

    # ------------------------------------------------------------------
    # Publishing
    # ------------------------------------------------------------------
    published = models.BooleanField(
        default=True,
        help_text="When False the item is hidden from parents.",
    )

    # ------------------------------------------------------------------
    # Timestamps
    # ------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Media Item"
        verbose_name_plural = "Media Items"
        indexes = [
            models.Index(fields=["organization", "kind", "published"]),
            models.Index(fields=["organization", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_kind_display()}] {self.title}"

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def save(self, *args, **kwargs):
        # Auto-fill file_name / mime_type from the uploaded file if absent.
        if self.file and not self.file_name:
            self.file_name = getattr(self.file, "name", "")
        super().save(*args, **kwargs)

    @property
    def youtube_url(self):
        if not self.youtube_id:
            return ""
        return f"https://www.youtube.com/watch?v={self.youtube_id}"

    def toggle_published(self):
        self.published = not self.published
        self.save(update_fields=["published", "updated_at"])
        return self.published

    @property
    def slug(self):
        return slugify(self.title)
    