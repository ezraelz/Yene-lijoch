from django.db import transaction
from rest_framework import serializers

from .models import Teacher
from users.models import Profile
from roles.models import Role
from organizations.models import Organization, OrganizationMembership


# ======================================================================
# Shared helper
# ======================================================================

def _resolve_organization(profile):
    """
    Profile.organization is an OrganizationMembership. Unwrap it to the
    actual Organization for API consumers.
    """
    membership = getattr(profile, "organization", None)
    if not membership:
        return None
    return getattr(membership, "organization", membership)


def _class_summary(classroom):
    return {
        "id": classroom.id,
        "name": classroom.name,
        "grade": getattr(classroom, "grade", ""),
        "student_count": classroom.students.count() if hasattr(classroom, "roster") else 0,
    }


# ======================================================================
# Read
# ======================================================================

class TeacherSerializer(serializers.ModelSerializer):
    """
    Admin-facing read serializer. Exposes the teacher's profile fields,
    organization (via profile), and employment date.
    """

    username = serializers.CharField(source="profile.username", read_only=True)
    email = serializers.EmailField(source="profile.email", read_only=True)
    first_name = serializers.CharField(source="profile.first_name", read_only=True)
    last_name = serializers.CharField(source="profile.last_name", read_only=True)
    full_name = serializers.CharField(source="full_name", read_only=True)
    profile_image = serializers.ImageField(source="profile.profile_image", read_only=True)
    sex = serializers.CharField(source="profile.sex", read_only=True)
    address = serializers.CharField(source="profile.address", read_only=True)
    contact = serializers.CharField(source="profile.contact", read_only=True)
    date_of_birth = serializers.DateField(source="profile.date_of_birth", read_only=True)

    organization = serializers.SerializerMethodField()
    organization_id = serializers.IntegerField(source="organization_id", read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",

            # Profile
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "profile_image",
            "sex",
            "address",
            "contact",
            "date_of_birth",

            # Organization (via profile.organization.organization)
            "organization",
            "organization_id",

            # Teacher
            "employment_date",
        ]
        read_only_fields = fields

    def get_organization(self, obj):
        org = obj.organization
        if not org:
            return None
        return {"id": org.id, "name": getattr(org, "name", "")}


# ======================================================================
# Me — what TeacherHome needs
# ======================================================================

class TeacherMeSerializer(serializers.ModelSerializer):
    """
    Shape consumed by `useTeacherData` on the frontend:

        {
          id, username, first_name, last_name, full_name, email,
          profile_image, contact, date_of_birth,
          organization: { id, name },
          employment_date,
          classes: [ { id, name, grade, student_count } ],
          program, group
        }

    `program` and `group` are UI concepts. If your schema has them on
    Profile or ClassRoom, adjust the getters below.
    """

    username = serializers.CharField(source="profile.username", read_only=True)
    email = serializers.EmailField(source="profile.email", read_only=True)
    first_name = serializers.CharField(source="profile.first_name", read_only=True)
    last_name = serializers.CharField(source="profile.last_name", read_only=True)
    profile_image = serializers.ImageField(source="profile.profile_image", read_only=True)
    contact = serializers.CharField(source="profile.contact", read_only=True)
    date_of_birth = serializers.DateField(source="profile.date_of_birth", read_only=True)

    organization = serializers.SerializerMethodField()
    classes = serializers.SerializerMethodField()
    program = serializers.SerializerMethodField()
    group = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "full_name",
            "email",
            "profile_image",
            "contact",
            "date_of_birth",
            "organization",
            "employment_date",
            "classes",
            "program",
            "group",
        ]

    def get_organization(self, obj):
        org = obj.organization
        if not org:
            return None
        return {"id": org.id, "name": getattr(org, "name", "")}

    def get_classes(self, obj):
        return [_class_summary(c) for c in obj.classes.all()]

    def get_program(self, obj):
        # Adjust if your schema stores "program" elsewhere.
        return getattr(obj.profile, "program", "Sunday School")

    def get_group(self, obj):
        # Frontend fallback: first class name, else empty.
        first = obj.classes.first()
        return first.name if first else ""


# ======================================================================
# Create (admin-side)
# ======================================================================

class TeacherCreateSerializer(serializers.ModelSerializer):
    """
    Links an existing Profile to a new Teacher row. Use
    `TeacherRegisterSerializer` when you want to create the Profile too.
    """

    profile = serializers.PrimaryKeyRelatedField(queryset=Profile.objects.all())

    class Meta:
        model = Teacher
        fields = ["profile", "employment_date"]
        extra_kwargs = {
            "employment_date": {"required": False},
        }


# ======================================================================
# Register (creates Profile + Teacher atomically)
# ======================================================================

class TeacherRegisterSerializer(serializers.ModelSerializer):

    teacher_details = TeacherCreateSerializer(write_only=True, required=False)

    class Meta:
        model = Profile
        fields = ["username", "email", "password", "teacher_details"]
        extra_kwargs = {
            "password": {"write_only": True, "required": True},
        }

    def validate_teacher_details(self, value):
        if not value:
            raise serializers.ValidationError("Teacher details are required.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        teacher_details = validated_data.pop("teacher_details")
        password = validated_data.pop("password")

        org = self.context.get("organization")
        role, _ = Role.objects.get_or_create(role_name="teacher")

        profile = Profile.objects.create(
            role=role,
            **validated_data,
        )
        profile.set_password(password)

        # Attach organization if provided.
        if org and hasattr(profile, "organization_id"):
            membership, _ = OrganizationMembership.objects.get_or_create(
                organization=org,
                user=profile,
            )
            profile.organization = membership

        profile.save()

        # teacher_details contains a `profile` key from the nested serializer.
        # Ignore it — we just created the profile.
        teacher_details.pop("profile", None)

        Teacher.objects.create(profile=profile, **teacher_details)
        return profile


# ======================================================================
# Edit
# ======================================================================

class TeacherEditSerializer(serializers.ModelSerializer):
    """
    Writes only fields that exist on the real model:
        - profile.* (via source="profile.x")
        - employment_date
    """

    username = serializers.CharField(source="profile.username", required=False)
    first_name = serializers.CharField(source="profile.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="profile.last_name", required=False, allow_blank=True)
    email = serializers.EmailField(source="profile.email", required=False, allow_blank=True)
    contact = serializers.CharField(source="profile.contact", required=False, allow_blank=True)
    date_of_birth = serializers.DateField(source="profile.date_of_birth", required=False, allow_null=True)
    address = serializers.CharField(source="profile.address", required=False, allow_blank=True)
    profile_image = serializers.ImageField(source="profile.profile_image", required=False, allow_null=True)

    class Meta:
        model = Teacher
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "contact",
            "date_of_birth",
            "address",
            "profile_image",
            "employment_date",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance
    