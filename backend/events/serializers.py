from datetime import datetime, time

from django.utils import timezone
from rest_framework import serializers

from .models import Event
from organizations.models import Organization


# ======================================================================
# Helpers
# ======================================================================

def _parse_time(value, default=time(10, 0)):
    """
    Accept '11:00 AM', '11:00', '11:00:00', or a time object.
    Falls back to `default` if it can't be parsed.
    """
    if value is None or value == "":
        return default
    if isinstance(value, time):
        return value
    if hasattr(value, "hour") and hasattr(value, "minute"):
        return value

    s = str(value).strip()
    for fmt in ("%I:%M %p", "%I:%M%p", "%H:%M:%S", "%H:%M"):
        try:
            return datetime.strptime(s, fmt).time()
        except ValueError:
            continue
    raise serializers.ValidationError(
        f"Could not parse time value: {value!r}. "
        "Use 'HH:MM' or 'HH:MM AM/PM'."
    )


def _parse_date(value, default=None):
    """
    Accept 'October 12, 2026', '2026-10-12', or a date object.
    """
    if value is None or value == "":
        return default
    if hasattr(value, "year") and hasattr(value, "month") and hasattr(value, "day"):
        return value

    s = str(value).strip()
    for fmt in (
        "%B %d, %Y",   # October 12, 2026
        "%b %d, %Y",   # Oct 12, 2026
        "%Y-%m-%d",    # 2026-10-12
        "%m/%d/%Y",    # 10/12/2026
    ):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise serializers.ValidationError(
        f"Could not parse date value: {value!r}. "
        "Use 'YYYY-MM-DD' or 'Month DD, YYYY'."
    )


def _localize(dt):
    """Attach the current timezone to a naive datetime."""
    if dt is None:
        return None
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt


# ======================================================================
# Read serializer (matches frontend Event shape)
# ======================================================================

class EventSerializer(serializers.ModelSerializer):
    """
    Read serializer.

    Exposes the exact shape the React Native frontend expects:
        { id, title, date, time, location, audience,
          description, status, published,
          start_datetime, end_datetime, event_type, image }
    """

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        allow_null=True,
    )

    # Frontend aliases -------------------------------------------------
    date = serializers.CharField(source="display_date", read_only=True)
    time = serializers.CharField(source="display_time", read_only=True)

    # Absolute image URL ----------------------------------------------
    image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            # identity
            "id",

            # ownership
            "organization",
            "organization_name",

            # frontend core fields
            "title",
            "date",           # alias for display_date
            "time",           # alias for display_time
            "location",
            "audience",
            "description",

            # status / publishing
            "status",
            "published",

            # scheduling (raw + labels)
            "start_datetime",
            "end_datetime",
            "date_label",
            "time_label",

            # misc
            "event_type",
            "image",

            # timestamps
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # this serializer is read-only

    def get_image(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        url = obj.image.url
        if request:
            return request.build_absolute_uri(url)
        return url


# ======================================================================
# Create serializer
# ======================================================================

class EventCreateSerializer(serializers.ModelSerializer):
    """
    Create serializer.

    Accepts BOTH:
      • the frontend's string fields:  date="October 12, 2026", time="11:00 AM"
      • the native Django split:       start_date / start_time /
                                       end_date / end_time

    `organization` is optional here and is normally injected by the view
    from `request.user` for non-superusers.
    """

    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True,
    )

    # Frontend-style write fields -------------------------------------
    date = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    time = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    # Native split fields ---------------------------------------------
    start_date = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    start_time = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    end_date = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )
    end_time = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Event
        fields = [
            "organization",

            "title",
            "description",
            "event_type",
            "location",
            "audience",

            # scheduling (both styles accepted)
            "date",
            "time",
            "start_date",
            "start_time",
            "end_date",
            "end_time",

            "date_label",
            "time_label",

            "status",
            "published",
            "image",
        ]
        extra_kwargs = {
            "title":       {"required": True},
            "description": {"required": False, "allow_blank": True},
            "location":    {"required": False, "allow_blank": True},
            "audience":    {"required": False, "allow_blank": True},
            "event_type":  {"required": False},
            "status":      {"required": False},
            "published":   {"required": False},
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_title(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Title is required.")
        return value

    def validate(self, data):
        # Merge the two date/time representations into start/end datetimes.
        start_datetime, end_datetime = self._resolve_datetimes(data)

        if end_datetime and end_datetime <= start_datetime:
            raise serializers.ValidationError({
                "end_datetime": "Event must end after it starts."
            })

        # Store the resolved values so create() can pop them.
        data["_start_datetime"] = start_datetime
        data["_end_datetime"] = end_datetime

        return data

    def _resolve_datetimes(self, data):
        """
        Prefer split (start_date/start_time) if present; otherwise use the
        frontend's string `date` / `time`.
        """
        # ----- start -----
        start_date_raw = data.pop("start_date", None)
        start_time_raw = data.pop("start_time", None)
        date_raw = data.pop("date", None)
        time_raw = data.pop("time", None)

        start_date = None
        start_time_val = None

        if start_date_raw:
            start_date = _parse_date(start_date_raw)
            start_time_val = _parse_time(start_time_raw)
        elif date_raw:
            # Frontend sends date and time as separate strings.
            start_date = _parse_date(date_raw)
            start_time_val = _parse_time(time_raw)

        if start_date is None:
            raise serializers.ValidationError({
                "start_datetime": "A start date is required."
            })

        start_datetime = _localize(
            datetime.combine(start_date, start_time_val)
        )

        # ----- end (optional) -----
        end_date_raw = data.pop("end_date", None)
        end_time_raw = data.pop("end_time", None)

        end_datetime = None
        if end_date_raw or end_time_raw:
            if end_date_raw and not end_time_raw:
                raise serializers.ValidationError({
                    "end_time": "End time is required when end date is provided."
                })
            if end_time_raw and not end_date_raw:
                raise serializers.ValidationError({
                    "end_date": "End date is required when end time is provided."
                })
            end_date = _parse_date(end_date_raw)
            end_time_val = _parse_time(end_time_raw)
            end_datetime = _localize(
                datetime.combine(end_date, end_time_val)
            )

        return start_datetime, end_datetime

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    def create(self, validated_data):
        org = self.context.get("organization")
        if org and not validated_data.get("organization"):
            validated_data["organization"] = org
        start_datetime = validated_data.pop("_start_datetime")
        end_datetime = validated_data.pop("_end_datetime", None)

        # Auto-fill attachment-style defaults if the client omitted them.
        validated_data.setdefault("location", Event.LOCATION_DEFAULT)
        validated_data.setdefault("audience", Event.AUDIENCE_DEFAULT)
        validated_data.setdefault("description", Event.DESCRIPTION_DEFAULT)

        # Auto-populate human labels from the resolved datetime if not given.
        if not validated_data.get("date_label"):
            validated_data["date_label"] = start_datetime.strftime("%B %d, %Y")
        if not validated_data.get("time_label"):
            validated_data["time_label"] = start_datetime.strftime("%I:%M %p")

        return Event.objects.create(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            **validated_data,
        )


# ======================================================================
# Edit serializer
# ======================================================================

class EventEditSerializer(serializers.ModelSerializer):
    """
    Update serializer (partial updates supported at the view level).
    Accepts the same date/time input styles as the create serializer.
    """

    date = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    time = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    start_date = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    start_time = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    end_date = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    end_time = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = Event
        fields = [
            "title",
            "description",
            "event_type",
            "location",
            "audience",

            "date",
            "time",
            "start_date",
            "start_time",
            "end_date",
            "end_time",

            "date_label",
            "time_label",

            "status",
            "published",
            "image",
        ]

    # ------------------------------------------------------------------
    def validate(self, data):
        instance = self.instance

        # Resolve start datetime (new value > instance fallback).
        start_date_raw = data.pop("start_date", None)
        start_time_raw = data.pop("start_time", None)
        date_raw = data.pop("date", None)
        time_raw = data.pop("time", None)

        start_datetime = None
        if start_date_raw:
            start_datetime = _localize(
                datetime.combine(
                    _parse_date(start_date_raw),
                    _parse_time(start_time_raw),
                )
            )
        elif date_raw:
            start_datetime = _localize(
                datetime.combine(
                    _parse_date(date_raw),
                    _parse_time(time_raw),
                )
            )
        elif instance:
            start_datetime = instance.start_datetime

        # Resolve end datetime.
        end_date_raw = data.pop("end_date", None)
        end_time_raw = data.pop("end_time", None)

        end_datetime = None
        if end_date_raw or end_time_raw:
            if end_date_raw and not end_time_raw:
                raise serializers.ValidationError({
                    "end_time": "End time is required when end date is provided."
                })
            if end_time_raw and not end_date_raw:
                raise serializers.ValidationError({
                    "end_date": "End date is required when end time is provided."
                })
            end_datetime = _localize(
                datetime.combine(
                    _parse_date(end_date_raw),
                    _parse_time(end_time_raw),
                )
            )
        elif instance:
            end_datetime = instance.end_datetime

        if start_datetime and end_datetime and end_datetime <= start_datetime:
            raise serializers.ValidationError({
                "end_datetime": "Event must end after it starts."
            })

        data["_start_datetime"] = start_datetime
        data["_end_datetime"] = end_datetime

        return data

    # ------------------------------------------------------------------
    def update(self, instance, validated_data):
        start_datetime = validated_data.pop("_start_datetime", None)
        end_datetime = validated_data.pop("_end_datetime", None)

        if start_datetime is not None:
            instance.start_datetime = start_datetime
            # Keep labels in sync if the client didn't send new ones.
            if "date_label" not in validated_data:
                instance.date_label = start_datetime.strftime("%B %d, %Y")
            if "time_label" not in validated_data:
                instance.time_label = start_datetime.strftime("%I:%M %p")

        if end_datetime is not None:
            instance.end_datetime = end_datetime

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
    