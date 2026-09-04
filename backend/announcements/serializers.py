from django.utils import timezone
from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):

    created_by_name = serializers.SerializerMethodField()
    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True
    )

    class Meta:
        model = Announcement
        fields = [
            "id",
            "organization",
            "organization_name",
            "title",
            "content",
            "audience",
            "priority",
            "created_by",
            "created_by_name",
            "is_published",
            "publish_at",
            "expires_at",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_by",
            "created_at",
            "updated_at",
            "organization_name",
            "created_by_name",
        ]

    def get_created_by_name(self, obj):
        if not obj.created_by:
            return None

        user = obj.created_by

        # If your custom User has first_name/last_name
        full_name = f"{user.first_name} {user.last_name}".strip()

        return full_name or user.username

    def validate(self, attrs):
        publish_at = attrs.get("publish_at")
        expires_at = attrs.get("expires_at")

        if publish_at and expires_at:
            if expires_at <= publish_at:
                raise serializers.ValidationError({
                    "expires_at": "Expiration time must be after the publication time."
                })

        return attrs
    