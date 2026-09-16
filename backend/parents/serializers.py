from rest_framework import serializers
import re

from .models import Parent
from users.models import Profile
from students.models import Student
from students.serializers import StudentSerializer
from roles.models import Role
from organizations.models import Organization

def sanitize_s_name(name: str) -> str:
    """Basic input sanitization for the display name (not the compare key)."""
    if not name:
        return ""
    # Strip any HTML/script content defensively; org names are plain text.
    text = re.sub(r"<[^>]*>", "", name)
    text = re.sub(r"\s+", " ", text).strip()
    return text

class ParentSearchSerializer(serializers.Serializer):
    q = serializers.CharField(min_length=2, max_length=150)

    def validate_q(self, value):
        return sanitize_s_name(value)

class ParentSerializer(serializers.ModelSerializer):

    # Profile fields
    username = serializers.CharField(
        source="profile.username",
        read_only=True
    )

    email = serializers.EmailField(
        source="profile.email",
        read_only=True
    )

    first_name = serializers.CharField(
        source="profile.first_name",
        read_only=True
    )

    last_name = serializers.CharField(
        source="profile.last_name",
        read_only=True
    )

    profile_image = serializers.ImageField(
        source="profile.profile_image",
        read_only=True
    )

    sex = serializers.CharField(
        source="profile.sex",
        read_only=True
    )

    address = serializers.CharField(
        source="profile.address",
        read_only=True
    )

    contact = serializers.CharField(
        source="profile.contact",
        read_only=True
    )

    date_of_birth = serializers.DateField(
        source="profile.date_of_birth",
        read_only=True
    )

    created_at = serializers.DateField(
        source="profile.created_at",
        read_only=True
    )

    status = serializers.BooleanField(
        source="profile.is_active",
        read_only=True
    )

    # Students
    student = StudentSerializer(
        many=True,
        read_only=True
    )

    student_name = serializers.SerializerMethodField()
    organization_name = serializers.CharField(
        source="profile.organization.name",
        read_only=True
    )

    class Meta:
        model = Parent

        fields = [
            "id",

            # Profile
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_image",
            "sex",
            "address",
            "contact",
            "date_of_birth",
            "created_at",
            "status",

            # Parent
            "organization_name",
            "student",
            "student_name",
            "relationship",
        ]

        read_only_fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_image",
            "sex",
            "address",
            "contact",
            "status",
            "date_of_birth",
            "created_at",
            "student",
            "student_name",
            "organization_name",
        ]

    def get_student_name(self, obj):
        return ", ".join(
            f"{student.profile.first_name} "
            f"{student.profile.last_name}"
            for student in obj.student.all()
        )


class ParentCreateSerializer(serializers.ModelSerializer):

    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = Parent

        fields = [
            "student",
            "relationship",
        ]

        extra_kwargs = {
            "student": {
                "required": True
            },
            "relationship": {
                "required": True
            },
        }

    def validate_student(self, value):

        if not value:
            raise serializers.ValidationError(
                "At least one student is required."
            )

        return value

class ParentRegisterSerializer(serializers.ModelSerializer):

    parent_details = ParentCreateSerializer(
        write_only=True,
        required=True
    )

    class Meta:
        model = Profile

        fields = [
            "username",
            "email",
            "password",
            "organization",
            "contact",
            "date_of_birth",
            "address",
            "parent_details",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True
            }
        }

    def validate_parent_details(self, value):

        if not value:
            raise serializers.ValidationError(
                "Parent details are required."
            )

        return value

    def create(self, validated_data):

        # Extract parent details
        parent_details = validated_data.pop(
            "parent_details"
        )

        # Extract password
        password = validated_data.pop(
            "password"
        )

        # Extract ManyToMany students
        students = parent_details.pop(
            "student",
            []
        )

        try:
            # Get/create parent role
            role, _ = Role.objects.get_or_create(
                role_name="parent"
            )

            # Create Profile
            profile = Profile.objects.create(
                **validated_data
            )

            # Set password
            profile.set_password(password)

            # Assign parent role
            profile.role = role

            profile.save()

            # Create Parent
            parent = Parent.objects.create(
                profile=profile,
                **parent_details
            )

            # Assign students
            if students:
                parent.student.set(students)

            return profile

        except Exception as e:

            # Rollback Profile if Parent creation fails
            if "profile" in locals():
                profile.delete()

            raise serializers.ValidationError({
                "parent_details": str(e)
            })


class ParentEditSerializer(serializers.ModelSerializer):

    parent_details = ParentCreateSerializer(
        write_only=True,
        required=False
    )

    class Meta:
        model = Profile
        
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "organization",
            "contact",
            "date_of_birth",
            "address",
            "parent_details",
        ]

    def update(self, instance, validated_data):

        # Extract parent details
        parent_details = validated_data.pop(
            "parent_details"
        )

        # Update Parent fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # Update students
        if parent_details is not None:
            instance.student.set(parent_details)

        return instance


