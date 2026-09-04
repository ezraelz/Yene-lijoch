from rest_framework import serializers

from .models import Event
from organizations.models import Organization


class EventSerializer(serializers.ModelSerializer):

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    class Meta:
        model = Event

        fields = [
            "id",
            "organization",
            "organization_name",
            "title",
            "description",
            "event_type",
            "location",
            "start_date",
            "end_date",
            "status",
            "image",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "church_name",
            "created_at",
            "updated_at",
        ]

class EventEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Event

        fields = [
            "organization",
            "title",
            "description",
            "event_type",
            "location",
            "start_date",
            "end_date",
            "status",
            "image",
        ]

    def validate(self, data):

        start_date = data.get(
            "start_date",
            self.instance.start_date if self.instance else None
        )

        end_date = data.get(
            "end_date",
            self.instance.end_date if self.instance else None
        )

        if start_date and end_date:
            if end_date <= start_date:
                raise serializers.ValidationError({
                    "end_date": "End date must be after start date."
                })

        return data

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

class EventCreateSerializer(serializers.ModelSerializer):

    start_date = serializers.DateField(write_only=True)
    start_time = serializers.TimeField(write_only=True)

    end_date = serializers.DateField(
        write_only=True,
        required=False
    )

    end_time = serializers.TimeField(
        write_only=True,
        required=False
    )

    class Meta:
        model = Event

        fields = [
            "organization",
            "title",
            "description",
            "event_type",
            "location",

            "start_date",
            "start_time",

            "end_date",
            "end_time",

            "status",
            "image",
        ]

    def validate(self, data):

        start_date = data.get("start_date")
        start_time = data.get("start_time")

        end_date = data.get("end_date")
        end_time = data.get("end_time")

        if end_date and not end_time:
            raise serializers.ValidationError({
                "end_time": "End time is required when end date is provided."
            })

        if end_time and not end_date:
            raise serializers.ValidationError({
                "end_date": "End date is required when end time is provided."
            })

        if end_date and end_time:

            from datetime import datetime

            start_datetime = datetime.combine(
                start_date,
                start_time
            )

            end_datetime = datetime.combine(
                end_date,
                end_time
            )

            if end_datetime <= start_datetime:
                raise serializers.ValidationError({
                    "end_date": "Event must end after it starts."
                })

        return data

    def create(self, validated_data):

        from datetime import datetime

        start_date = validated_data.pop("start_date")
        start_time = validated_data.pop("start_time")

        end_date = validated_data.pop("end_date", None)
        end_time = validated_data.pop("end_time", None)

        validated_data["start_datetime"] = datetime.combine(
            start_date,
            start_time
        )

        if end_date and end_time:
            validated_data["end_datetime"] = datetime.combine(
                end_date,
                end_time
            )

        return Event.objects.create(
            **validated_data
        )
    