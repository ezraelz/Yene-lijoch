from rest_framework import serializers

from .models import Student
from users.models import Profile
from organizations.models import Organization
from organizations.serializers import OrganizationSummarySerializer
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

    organization = OrganizationSummarySerializer(read_only=True)

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
            "organization",
            "guardian_name",
            "guardian_contact",
            "status",
            "enrollment_date",
        ]

        read_only_fields = [
            "id",
        ]

class StudentCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student

        fields = [
            "organization",
            "guardian_name",
            "guardian_contact",
            "status",
            "enrollment_date",
        ]

        extra_kwargs = {
            "organization": {
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


# students/serializers.py

class StudentEditSerializer(serializers.ModelSerializer):
    """
    Serializer for editing student data.
    Works with Student model but updates both Profile and Student.
    """
    
    # These fields will come from the request with these exact names
    # We use source to tell DRF where to save them
    username = serializers.CharField(source='profile.username', required=False, allow_blank=True)
    email = serializers.EmailField(source='profile.email', required=False, allow_blank=True)
    first_name = serializers.CharField(source='profile.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='profile.last_name', required=False, allow_blank=True)
    profile_image = serializers.ImageField(source='profile.profile_image', required=False, allow_null=True)
    sex = serializers.CharField(source='profile.sex', required=False, allow_blank=True, allow_null=True)
    address = serializers.CharField(source='profile.address', required=False, allow_blank=True)
    contact = serializers.CharField(source='profile.contact', required=False, allow_blank=True)
    date_of_birth = serializers.DateField(source='profile.date_of_birth', required=False, allow_null=True)
    
    # Student fields (no source needed)
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,
        allow_null=True
    )
    guardian_name = serializers.CharField(required=False, allow_blank=True)
    guardian_contact = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(required=False)
    enrollment_date = serializers.DateField(required=False, allow_null=True)

    class Meta:
        model = Student
        fields = [
            # Profile fields
            "username",
            "email",
            "first_name",
            "last_name",
            "profile_image",
            "sex",
            "address",
            "contact",
            "date_of_birth",
            # Student fields
            "organization",
            "guardian_name",
            "guardian_contact",
            "status",
            "enrollment_date",
        ]

    def update(self, instance, validated_data):
        # DRF automatically nests profile fields under 'profile' key
        # because of the source='profile.field_name'
        profile_data = validated_data.pop('profile', {})
        # Update Profile
        profile = instance.profile
        
        # Handle each profile field
        if 'username' in profile_data:
            profile.username = profile_data['username']
        if 'email' in profile_data:
            profile.email = profile_data['email']
        if 'first_name' in profile_data:
            profile.first_name = profile_data['first_name']
        if 'last_name' in profile_data:
            profile.last_name = profile_data['last_name']
        if 'profile_image' in profile_data:
            profile.profile_image = profile_data['profile_image']
        if 'sex' in profile_data:
            profile.sex = profile_data['sex']
        if 'address' in profile_data:
            profile.address = profile_data['address']
        if 'contact' in profile_data:
            profile.contact = profile_data['contact']
        if 'date_of_birth' in profile_data:
            profile.date_of_birth = profile_data['date_of_birth']
        profile.save()
        # Update Student fields (these are at the top level)
        if 'organization' in validated_data:
            instance.organization = validated_data['organization']
        if 'guardian_name' in validated_data:
            instance.guardian_name = validated_data['guardian_name']
        if 'guardian_contact' in validated_data:
            instance.guardian_contact = validated_data['guardian_contact']
        if 'status' in validated_data:
            instance.status = validated_data['status']
        if 'enrollment_date' in validated_data:
            instance.enrollment_date = validated_data['enrollment_date']
        instance.save()
        # Refresh to get updated data
        instance.refresh_from_db()
        return instance
    
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

        