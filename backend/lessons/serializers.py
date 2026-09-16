from rest_framework import serializers
from django.utils import timezone

from .models import Lesson
from classes.models import ClassRoom

# ======================================================================
# Read serializer (matches frontend SharedCurriculum shape)
# ======================================================================

class LessonSerializer(serializers.ModelSerializer):
    """
    Read serializer used by the React Native admin + parent apps.

    Exposes camelCase aliases so the payload matches the frontend's
    SharedCurriculum type:
        { id, title, category, week, date, year, scripture,
          memoryVerse, description, status, published,
          coverUri, attachmentUri, attachmentName, attachmentType }
    """

    # -- Related names -------------------------------------------------
    classroom_name = serializers.CharField(
        source="classroom.name",
        read_only=True,
        allow_null=True,
    )

    # -- Frontend aliases ---------------------------------------------
    date = serializers.CharField(source="display_date", read_only=True)
    memoryVerse = serializers.CharField(source="memory_verse", read_only=True)

    # -- Media URLs ----------------------------------------------------
    coverUri = serializers.SerializerMethodField()
    attachmentUri = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = [
            # identity
            "id",

            # relationships
            "classroom",
            "classroom_name",

            # frontend core fields
            "title",
            "category",
            "week",
            "date",           # alias for display_date
            "year",
            "lesson_date",
            "date_label",

            # body
            "scripture",
            "memoryVerse",    # alias for memory_verse
            "memory_verse",
            "description",

            # status / publishing
            "status",
            "published",

            # media
            "coverUri",
            "attachmentUri",
            "attachment_name",
            "attachment_type",

            # timestamps
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # this serializer is read-only

    # ------------------------------------------------------------------
    # Method fields
    # ------------------------------------------------------------------

    def _absolute_url(self, file_field):
        if not file_field:
            return None
        request = self.context.get("request")
        url = file_field.url
        if request:
            return request.build_absolute_uri(url)
        return url

    def get_coverUri(self, obj):
        return self._absolute_url(obj.cover)

    def get_attachmentUri(self, obj):
        return self._absolute_url(obj.attachment)


# ======================================================================
# Write serializers
# ======================================================================

class LessonCreateSerializer(serializers.ModelSerializer):
    """
    Create serializer.

    Accepts both snake_case (native Django) and the frontend's camelCase
    aliases (memoryVerse). `year` is derived from `lesson_date`, so it is
    not required from the client.
    """

    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        required=False,
        allow_null=True,
    )

    # Accept the frontend's camelCase field name.
    memoryVerse = serializers.CharField(
        source="memory_verse",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Lesson
        fields = [
            "classroom",

            "title",
            "category",
            "week",

            "lesson_date",
            "date_label",
            "year",           # optional; overwritten in save()

            "start_time",
            "end_time",

            "scripture",
            "memoryVerse",    # maps to memory_verse
            "memory_verse",
            "description",
            "objective",
            "materials", 
            "activity",

            "content",
            "objectives",

            "status",
            "published",

            "cover",
            "attachment",
            "attachment_name",
            "attachment_type",
        ]
        extra_kwargs = {
            "title":       {"required": True},
            "lesson_date": {"required": True},
            "year":        {"required": False},
            "category":    {"required": False},
            "week":        {"required": False},
            "scripture":   {"required": False},
            "description": {"required": False},
            "status":      {"required": False},
            "published":   {"required": False},
        }

    # ------------------------------------------------------------------
    # Field-level validation
    # ------------------------------------------------------------------
    def validate_week(self, value):
        if value is not None and not (1 <= value <= 53):
            raise serializers.ValidationError(
                "Week must be between 1 and 53."
            )
        return value

    def validate_lesson_date(self, value):
        if value and value.year < 2000:
            raise serializers.ValidationError(
                "Lesson date must be in the year 2000 or later."
            )
        return value

    # ------------------------------------------------------------------
    # Object-level validation
    # ------------------------------------------------------------------
    def validate(self, data):
        classroom = data.get("classroom")

        start_time = data.get("start_time")
        end_time = data.get("end_time")

        # End time requires a start time.
        if end_time and not start_time:
            raise serializers.ValidationError({
                "start_time":
                    "Start time is required when end time is provided."
            })

        # End time must be after start time.
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })

        # Prevent duplicate (classroom, year, week) when classroom is set.
        lesson_date = data.get("lesson_date")
        week = data.get("week")
        if classroom and lesson_date and week is not None:
            qs = Lesson.objects.filter(
                classroom=classroom,
                year=lesson_date.year,
                week=week,
            )
            if qs.exists():
                raise serializers.ValidationError({
                    "week":
                        f"A lesson already exists for week {week} "
                        f"of {lesson_date.year} in this classroom."
                })

        return data

    def create(self, validated_data):
        # `year` is always derived from `lesson_date`.
        if validated_data.get("lesson_date"):
            validated_data["year"] = validated_data["lesson_date"].year

        # Populate attachment_name from uploaded file if missing.
        attachment = validated_data.get("attachment")
        if attachment and not validated_data.get("attachment_name"):
            validated_data["attachment_name"] = getattr(
                attachment, "name", ""
            )

        return super().create(validated_data)


class LessonEditSerializer(serializers.ModelSerializer):
    """
    Update serializer (partial by default at the view level).
    """

    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        required=False,
        allow_null=True,
    )

    memoryVerse = serializers.CharField(
        source="memory_verse",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Lesson
        fields = [
            "classroom",

            "title",
            "category",
            "week",

            "lesson_date",
            "date_label",
            "year",

            "start_time",
            "end_time",

            "scripture",
            "memoryVerse",
            "memory_verse",
            "description",
            "objective",
            "materials", 
            "activity",

            "content",
            "objectives",

            "status",
            "published",

            "cover",
            "attachment",
            "attachment_name",
            "attachment_type",
        ]

    # ------------------------------------------------------------------
    # Field-level validation
    # ------------------------------------------------------------------
    def validate_week(self, value):
        if value is not None and not (1 <= value <= 53):
            raise serializers.ValidationError(
                "Week must be between 1 and 53."
            )
        return value

    # ------------------------------------------------------------------
    # Object-level validation
    # ------------------------------------------------------------------
    def validate(self, data):
        instance = self.instance

        # Resolve effective values (data → instance fallback).
        classroom = data.get("classroom", getattr(instance, "classroom", None))

        start_time = data.get(
            "start_time", getattr(instance, "start_time", None)
        )
        end_time = data.get(
            "end_time", getattr(instance, "end_time", None)
        )

        # Time ordering.
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError({
                "end_time": "End time must be after start time."
            })

        # Duplicate (classroom, year, week) check.
        lesson_date = data.get(
            "lesson_date", getattr(instance, "lesson_date", None)
        )
        week = data.get("week", getattr(instance, "week", None))

        if classroom and lesson_date and week is not None:
            qs = Lesson.objects.filter(
                classroom=classroom,
                year=lesson_date.year,
                week=week,
            ).exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "week":
                        f"A lesson already exists for week {week} "
                        f"of {lesson_date.year} in this classroom."
                })

        return data

    def update(self, instance, validated_data):
        # Re-derive year if the date changed.
        if "lesson_date" in validated_data and validated_data["lesson_date"]:
            validated_data["year"] = validated_data["lesson_date"].year

        # Refresh attachment_name if a new file was uploaded.
        attachment = validated_data.get("attachment")
        if attachment and not validated_data.get("attachment_name"):
            validated_data["attachment_name"] = getattr(
                attachment, "name", ""
            )

        return super().update(instance, validated_data)


class LessonTeacherSerializer(serializers.ModelSerializer):
    """
    Read-only shape for the teacher app.
    """

    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    classroom_id = serializers.IntegerField(source="classroom.id", read_only=True)

    date = serializers.CharField(source="display_date", read_only=True)
    memoryVerse = serializers.CharField(source="memory_verse", read_only=True)

    coverUri = serializers.SerializerMethodField()
    attachmentUri = serializers.SerializerMethodField()

    objective = serializers.CharField(read_only=True)
    materials = serializers.JSONField(read_only=True)
    activity = serializers.CharField(read_only=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "title",
            "category",
            "week",
            "year",

            # Scheduling — only these three exist on the refined model.
            "date",           # alias for display_date
            "lesson_date",
            "date_label",

            # Content
            "scripture",
            "memoryVerse",
            "memory_verse",
            "description",
            "objective", 
            "materials", 
            "activity",

            # Classroom
            "classroom_id",
            "classroom_name",

            # Status
            "status",
            "published",

            # Media
            "coverUri",
            "attachmentUri",
            "attachment_name",
            "attachment_type",
        ]

    def _abs(self, f):
        if not f:
            return None
        request = self.context.get("request")
        url = f.url
        return request.build_absolute_uri(url) if request else url

    def get_coverUri(self, obj):
        return self._abs(obj.cover)

    def get_attachmentUri(self, obj):
        return self._abs(obj.attachment)

    