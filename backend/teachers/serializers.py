from rest_framework import serializers

from .models import Teacher
from users.models import Profile
from roles.models import Role


class TeacherSerializer(serializers.ModelSerializer):

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
        model = Teacher

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

            # Teacher
            "organization",
            "employment_date",
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
            "subject",
            "subject_name",
        ]

    def get_subject_name(self, obj):
        return ", ".join(
            course.course_name
            for course in obj.subject.all()
        )

class TeacherEditSerializer(serializers.ModelSerializer):

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
        model = Teacher

        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_image",
            "sex",
            "address",
            "contact",
            "date_of_birth",

            "organization",
            "employment_date",
        ]

    def update(self, instance, validated_data):
        # Update Teacher fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance

class TeacherCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Teacher

        fields = [
            "organization",
            "employment_date",
        ]

        extra_kwargs = {
            "organization": {
                "required": True
            },
            "employment_date": {
                "required": True
            }
        }

class TeacherRegisterSerializer(serializers.ModelSerializer):

    teacher_details = TeacherCreateSerializer(
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
            "teacher_details",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "required": True
            }
        }

    def validate_teacher_details(self, value):

        if not value:
            raise serializers.ValidationError(
                "Teacher details are required."
            )

        return value

    def create(self, validated_data):

        # Separate teacher data
        teacher_details = validated_data.pop(
            "teacher_details"
        )

        # Get password
        password = validated_data.pop(
            "password"
        )

        try:
            # Get or create teacher role
            role, _ = Role.objects.get_or_create(
                role_name="teacher"
            )

            # Create Profile
            profile = Profile.objects.create(
                **validated_data
            )

            # Set password securely
            profile.set_password(password)

            # Assign teacher role
            profile.role = role

            profile.save()

            # Create Teacher
            teacher = Teacher.objects.create(
                profile=profile,
                **teacher_details
            )

            return profile

        except Exception as e:

            # Rollback profile if teacher creation fails
            if "profile" in locals():
                profile.delete()

            raise serializers.ValidationError({
                "teacher_details": str(e)
            })
        