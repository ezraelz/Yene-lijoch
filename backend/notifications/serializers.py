from rest_framework import serializers

from .models import Notification, PushToken


class NotificationSerializer(serializers.ModelSerializer):
    actor_id = serializers.IntegerField(source="actor.id", read_only=True, default=None)

    class Meta:
        model = Notification
        fields = [
            "id",
            "notification_type",
            "title",
            "body",
            "data",
            "read",
            "created_at",
            "actor_id",
        ]
        read_only_fields = fields


class PushTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = PushToken
        fields = ["token", "platform"]

    def validate_token(self, value):
        if not value:
            raise serializers.ValidationError("token is required.")
        return value
