from rest_framework import serializers

from .models import Role, Permission


class PermissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission

        fields = [
            "id",
            "name",
            "codename",
            "category",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "Permission name cannot be empty."
            )

        return value

    def validate_codename(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Permission codename cannot be empty."
            )

        return value

    def validate_category(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Permission category cannot be empty."
            )

        return value


class RoleSerializer(serializers.ModelSerializer):

    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.filter(is_active=True),
        required=False,
    )

    permission_details = PermissionSerializer(
        source="permissions",
        many=True,
        read_only=True,
    )

    permission_count = serializers.SerializerMethodField()

    class Meta:
        model = Role

        fields = [
            "id",
            "role_name",
            "description",
            "is_active",
            "permissions",
            "permission_details",
            "permission_count",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "permission_details",
            "permission_count",
            "created_at",
            "updated_at",
        ]

    def validate_role_name(self, value):
        value = value.strip().lower()

        if not value:
            raise serializers.ValidationError(
                "Role name cannot be empty."
            )

        return value

    def get_permission_count(self, obj):
        return obj.permissions.count()
    