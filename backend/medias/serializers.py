from rest_framework import serializers

from .models import MediaItem
from organizations.models import Organization


# ======================================================================
# Helpers
# ======================================================================

def _extract_youtube_id(value):
    """
    Accept a full YouTube URL or a bare ID and return just the ID.

    Mirrors the frontend's `extractId()`:
        https://www.youtube.com/watch?v=abc123  → abc123
        https://youtu.be/abc123                 → abc123
        https://www.youtube.com/embed/abc123    → abc123
        abc123                                  → abc123
    """
    if not value:
        return ""
    value = str(value).strip()
    if not value:
        return ""

    import re
    match = re.search(
        r"(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{6,})",
        value,
    )
    return match.group(1) if match else value


def _validate_kind(value):
    """Ensure kind is one of the model's choices."""
    valid = {choice[0] for choice in MediaItem.KIND_CHOICES}
    if value not in valid:
        raise serializers.ValidationError(
            f"Invalid kind '{value}'. Must be one of: {', '.join(sorted(valid))}."
        )
    return value


def _validate_source(value):
    valid = {choice[0] for choice in MediaItem.SOURCE_CHOICES}
    if value not in valid:
        raise serializers.ValidationError(
            f"Invalid source '{value}'. Must be one of: {', '.join(sorted(valid))}."
        )
    return value


# ======================================================================
# Read serializer (matches frontend MediaItem shape)
# ======================================================================

class MediaItemSerializer(serializers.ModelSerializer):
    """
    Read serializer.

    Exposes the exact shape AdminVideosScreen.js (and parent screens)
    expect:
        { id, title, kind, youtubeId, duration, ageGroup, description,
          published, source, coverUri, fileUri, fileName, mimeType }
    """

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        allow_null=True,
    )

    # camelCase aliases matching the frontend -------------------------
    youtubeId = serializers.CharField(source="youtube_id", read_only=True)
    ageGroup = serializers.CharField(source="age_group", read_only=True)
    fileName = serializers.CharField(source="file_name", read_only=True)
    mimeType = serializers.CharField(source="mime_type", read_only=True)

    # Absolute URLs for the media itself ------------------------------
    coverUri = serializers.SerializerMethodField()
    fileUri = serializers.SerializerMethodField()

    class Meta:
        model = MediaItem
        fields = [
            # identity
            "id",

            # ownership
            "organization",
            "organization_name",

            # frontend core fields
            "title",
            "kind",
            "youtubeId",
            "duration",
            "ageGroup",
            "description",

            # publishing
            "published",
            "source",

            # media
            "coverUri",
            "fileUri",
            "fileName",
            "mimeType",

            # raw snake_case (useful for admin/debug)
            "youtube_id",
            "age_group",

            # timestamps
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # fully read-only

    # ------------------------------------------------------------------
    def _absolute_url(self, file_field):
        if not file_field:
            return None
        url = file_field.url
        request = self.context.get("request")
        return request.build_absolute_uri(url) if request else url

    def get_coverUri(self, obj):
        return self._absolute_url(obj.cover)

    def get_fileUri(self, obj):
        return self._absolute_url(obj.file)


# ======================================================================
# Create serializer
# ======================================================================

class MediaItemCreateSerializer(serializers.ModelSerializer):
    """
    Create serializer.

    Accepts the frontend's camelCase payload:
        { title, kind, youtubeId, duration, ageGroup, description,
          published, source, coverUri?, fileName?, mimeType? }

    The actual binary uploads (`file`, `cover`) come through as
    multipart form fields.

    `organization` is normally injected by the view from
    `request.user`; superusers may pass it explicitly.
    """

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
    )

    # camelCase write fields (mapped to model fields) -----------------
    youtubeId = serializers.CharField(
        source="youtube_id",
        required=False,
        allow_blank=True,
    )
    ageGroup = serializers.CharField(
        source="age_group",
        required=False,
        allow_blank=True,
    )
    fileName = serializers.CharField(
        source="file_name",
        required=False,
        allow_blank=True,
    )
    mimeType = serializers.CharField(
        source="mime_type",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = MediaItem
        fields = [
            "organization",

            "title",
            "kind",
            "youtubeId",
            "duration",
            "ageGroup",
            "description",

            "published",
            "source",

            "file",
            "cover",
            "fileName",
            "mimeType",
        ]
        extra_kwargs = {
            "title":       {"required": True},
            "kind":        {"required": False},
            "duration":    {"required": False, "allow_blank": True},
            "description": {"required": False, "allow_blank": True},
            "published":   {"required": False},
            "source":      {"required": False},
            "file":        {"required": False, "allow_null": True},
            "cover":       {"required": False, "allow_null": True},
        }

    # ------------------------------------------------------------------
    # Field-level validation
    # ------------------------------------------------------------------
    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Title is required.")
        return value

    def validate_kind(self, value):
        return _validate_kind(value)

    def validate_source(self, value):
        return _validate_source(value)

    def validate_youtubeId(self, value):
        # Normalise a full URL down to just the ID.
        return _extract_youtube_id(value)

    # ------------------------------------------------------------------
    # Object-level validation
    # ------------------------------------------------------------------
    def validate(self, data):
        kind = data.get("kind", MediaItem.KIND_VIDEO)
        source = data.get("source", MediaItem.SOURCE_GALLERY)
        youtube_id = data.get("youtube_id", "")
        file = data.get("file")
        cover = data.get("cover")

        # ----- Rule 1: a media item must have *something* -----------
        has_gallery = bool(file or cover)
        has_youtube = bool(youtube_id)

        if not has_gallery and not has_youtube:
            raise serializers.ValidationError({
                "non_field_errors":
                    "Provide a file upload or a YouTube link."
            })

        # ----- Rule 2: picture requires an image --------------------
        if kind == MediaItem.KIND_PICTURE and not (cover or file):
            raise serializers.ValidationError({
                "cover": "A picture item requires an image."
            })

        # ----- Rule 3: source consistency ---------------------------
        if has_youtube and not has_gallery:
            data["source"] = MediaItem.SOURCE_YOUTUBE
        elif has_gallery and not has_youtube:
            data["source"] = MediaItem.SOURCE_GALLERY
        # If both are present, trust the client's `source`.

        return data

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create(self, validated_data):
        org = self.context.get("organization")
        if org and not validated_data.get("organization"):
            validated_data["organization"] = org
        # Auto-fill defaults matching the frontend's own fallbacks.
        validated_data.setdefault("duration", "3:00")
        validated_data.setdefault("age_group", "All ages")
        validated_data.setdefault("kind", MediaItem.KIND_VIDEO)
        validated_data.setdefault("source", MediaItem.SOURCE_GALLERY)

        if not validated_data.get("description"):
            kind = validated_data["kind"]
            label = dict(MediaItem.KIND_CHOICES).get(kind, kind)
            validated_data["description"] = (
                f"Uploaded for parents in {label}."
            )

        # Auto-fill file_name / mime_type from the uploaded file.
        file = validated_data.get("file")
        if file and not validated_data.get("file_name"):
            validated_data["file_name"] = getattr(file, "name", "")

        return MediaItem.objects.create(**validated_data)


# ======================================================================
# Edit serializer
# ======================================================================

class MediaItemEditSerializer(serializers.ModelSerializer):
    """
    Update serializer (partial updates supported at the view level).
    """

    youtubeId = serializers.CharField(
        source="youtube_id",
        required=False,
        allow_blank=True,
    )
    ageGroup = serializers.CharField(
        source="age_group",
        required=False,
        allow_blank=True,
    )
    fileName = serializers.CharField(
        source="file_name",
        required=False,
        allow_blank=True,
    )
    mimeType = serializers.CharField(
        source="mime_type",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = MediaItem
        fields = [
            "title",
            "kind",
            "youtubeId",
            "duration",
            "ageGroup",
            "description",

            "published",
            "source",

            "file",
            "cover",
            "fileName",
            "mimeType",
        ]
        extra_kwargs = {
            "title":       {"required": False},
            "kind":        {"required": False},
            "duration":    {"required": False, "allow_blank": True},
            "description": {"required": False, "allow_blank": True},
            "published":   {"required": False},
            "source":      {"required": False},
            "file":        {"required": False, "allow_null": True},
            "cover":       {"required": False, "allow_null": True},
        }

    # ------------------------------------------------------------------
    def validate_kind(self, value):
        return _validate_kind(value)

    def validate_source(self, value):
        return _validate_source(value)

    def validate_youtubeId(self, value):
        return _extract_youtube_id(value)

    # ------------------------------------------------------------------
    def validate(self, data):
        instance = self.instance

        # Resolve effective values (incoming > instance).
        kind = data.get("kind", getattr(instance, "kind", MediaItem.KIND_VIDEO))
        youtube_id = data.get("youtube_id", getattr(instance, "youtube_id", ""))
        file = data.get("file", getattr(instance, "file", None))
        cover = data.get("cover", getattr(instance, "cover", None))

        has_gallery = bool(file or cover)
        has_youtube = bool(youtube_id)

        if not has_gallery and not has_youtube:
            raise serializers.ValidationError({
                "non_field_errors":
                    "A media item must keep a file upload or a YouTube link."
            })

        if kind == MediaItem.KIND_PICTURE and not (cover or file):
            raise serializers.ValidationError({
                "cover": "A picture item requires an image."
            })

        return data

    # ------------------------------------------------------------------
    def update(self, instance, validated_data):
        # Refresh file_name when a new file is uploaded.
        file = validated_data.get("file")
        if file and not validated_data.get("file_name"):
            instance.file_name = getattr(file, "name", "")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    