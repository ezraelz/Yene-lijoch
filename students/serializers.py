from rest_framework import serializers

from .models import Student
from users.models import Profile
from churches.models import Church
from roles.models import Role


class StudentSerializer(serializers.ModelSerializer):

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

    class Meta:
        model = Student

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

            # Student
            "church",
            "guardian_name",
            "guardian_contact",
            "status",
            "enrollment_date",
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
            "date_of_birth",
        ]

class StudentEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student

        fields = [
            "church",
            "guardian_name",
            "guardian_contact",
            "status",
            "enrollment_date",
        ]

    def update(self, instance, validated_data):

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

class StudentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student

        fields = [
            "church",
            "guardian_name",
            "guardian_contact",
            "status",
            "enrollment_date",
        ]

        extra_kwargs = {
            "church": {
                "required": True
            },
            "guardian_name": {
                "required": True
            },
            "guardian_contact": {
                "required": True
            },
            "enrollment_date": {
                "required": True
            },
        }


class StudentRegisterSerializer(serializers.ModelSerializer):

    student_details = StudentCreateSerializer(
        write_only=True,
        required=True
    )

    class Meta:
        model = Profile

        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "contact",
            "date_of_birth",
            "address",
            "student_details",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True
            }
        }

    def validate_student_details(self, value):

        if not value:
            raise serializers.ValidationError(
                "Student details are required."
            )

        return value

    def create(self, validated_data):

        # Extract student data
        student_details = validated_data.pop(
            "student_details"
        )

        # Extract password
        password = validated_data.pop(
            "password"
        )

        try:
            # Get or create student role
            role, _ = Role.objects.get_or_create(
                role_name="student"
            )

            # Create Profile
            profile = Profile.objects.create(
                **validated_data
            )

            # Set password securely
            profile.set_password(password)

            # Assign student role
            profile.role = role

            profile.save()

            # Create Student
            student = Student.objects.create(
                profile=profile,
                **student_details
            )

            return profile

        except Exception as e:

            # Rollback profile if student creation fails
            if "profile" in locals():
                profile.delete()

            raise serializers.ValidationError({
                "student_details": str(e)
            })
        