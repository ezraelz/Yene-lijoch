import re

from django.db import transaction
from rest_framework import serializers

from .models import Student
from classes.models import ClassRoom
from users.models import Profile
from organizations.models import Organization
from organizations.serializers import OrganizationSummarySerializer
from roles.models import Role


# ======================================================================
# Helpers
# ======================================================================

def sanitize_name(name: str) -> str:
    """Strip HTML and collapse whitespace in a display name."""
    if not name:
        return ""
    text = re.sub(r"<[^>]*>", "", name)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def split_full_name(full_name: str):
    """
    Split 'Ruth Bekele' into ('Ruth', 'Bekele').
    Single-token names → ('Ruth', '').
    """
    parts = sanitize_name(full_name).split(maxsplit=1)
    if not parts:
        return "", ""
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def get_organization_from_context(context):
    """
    Resolve the organization from context, tolerating both
    `Organization` and `OrganizationMembership` shapes.
    """
    org = context.get("organization")
    if not org:
        return None
    # If it's a membership, unwrap to the actual org.
    return getattr(org, "organization", org)


# ======================================================================
# Read serializer (matches frontend Student shape)
# ======================================================================

class StudentSerializer(serializers.ModelSerializer):
    """
    Read serializer.

    Exposes the frontend's Student shape on top of the Profile model:
        { id, name, groupId, grade, age, parentName, parentEmail, status }

    Plus every Profile field for admin tooling.
    """

    # ----- Profile-derived fields -------------------------------------
    name = serializers.SerializerMethodField()
    first_name = serializers.CharField(source="profile.first_name", read_only=True)
    last_name = serializers.CharField(source="profile.last_name", read_only=True)
    full_name = serializers.CharField(source="profile.full_name", read_only=True)
    username = serializers.CharField(source="profile.username", read_only=True)
    email = serializers.EmailField(source="profile.email", read_only=True)
    profile_image = serializers.ImageField(source="profile.profile_image", read_only=True)
    sex = serializers.CharField(source="profile.sex", read_only=True)
    address = serializers.CharField(source="profile.address", read_only=True)
    contact = serializers.CharField(source="profile.contact", read_only=True)
    date_of_birth = serializers.DateField(source="profile.date_of_birth", read_only=True)
    profile_organization = OrganizationSummarySerializer(
        source="profile.organization",
        read_only=True,
    )

    # ----- Student-side aliases matching the frontend -----------------
    groupId = serializers.PrimaryKeyRelatedField(
        source="classroom",
        read_only=True,
    )
    group_name = serializers.SerializerMethodField()
    parentName = serializers.CharField(source="guardian_name", read_only=True)
    parentEmail = serializers.EmailField(source="guardian_email", read_only=True)

    class Meta:
        model = Student
        fields = [
            "id",

            # frontend aliases
            "name",
            "groupId",
            "group_name",
            "grade",
            "age",
            "parentName",
            "parentEmail",

            # Profile (full)
            "first_name",
            "last_name",
            "full_name",
            "username",
            "email",
            "profile_image",
            "sex",
            "address",
            "contact",
            "date_of_birth",
            "profile_organization",

            # Student lifecycle
            "organization",
            "guardian_name",
            "guardian_email",
            "guardian_contact",
            "status",
            "enrollment_date",

            # timestamps
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields  # fully read-only

    # ------------------------------------------------------------------
    def get_name(self, obj):
        return obj.full_name

    def get_group_name(self, obj):
        return obj.classroom.name if obj.classroom_id else ""


# ======================================================================
# Summary serializer (search / dup-check)
# ======================================================================

class StudentSummarySerializer(serializers.ModelSerializer):
    """
    Lightweight summary used in search/dup-check results. Omits internal
    fields so we don't leak who submitted a record to other users.
    """

    full_name = serializers.CharField(source="profile.full_name", read_only=True)
    similarity = serializers.FloatField(read_only=True, required=False)

    class Meta:
        model = Student
        fields = ["id", "full_name", "status", "similarity"]
        read_only_fields = fields


# ======================================================================
# Search input
# ======================================================================

class StudentSearchSerializer(serializers.Serializer):
    q = serializers.CharField(min_length=2, max_length=150)

    def validate_q(self, value):
        return sanitize_name(value)


# ======================================================================
# Create serializer
# ======================================================================

class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Create serializer.

    Accepts the frontend's addStudent payload:
        { name, groupId, grade, age, parentName, parentEmail }

    Also accepts an optional `profile_id` so callers who already have a
    Profile (e.g. a pre-registered user) can link it instead of having
    one created on the fly.
    """

    # Frontend aliases -------------------------------------------------
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    groupId = serializers.PrimaryKeyRelatedField(
        source="classroom",
        queryset=ClassRoom.objects.all(),
        required=False,
        allow_null=True,
    )
    parentName = serializers.CharField(
        source="guardian_name",
        required=False,
        allow_blank=True,
    )
    parentEmail = serializers.EmailField(
        source="guardian_email",
        required=False,
        allow_blank=True,
    )

    # Optional: attach an existing Profile instead of creating one -----
    profile_id = serializers.PrimaryKeyRelatedField(
        source="profile",
        queryset=Profile.objects.all(),
        required=False,
        allow_null=True,
        write_only=True,
    )

    # Age is an IntegerField on the model; accept strings from the UI --
    age = serializers.IntegerField(
        required=False,
        allow_null=True,
        min_value=1,
        max_value=100,
    )

    class Meta:
        model = Student
        fields = [
            "name",
            "groupId",
            "grade",
            "age",
            "parentName",
            "parentEmail",
            "profile_id",
            "guardian_contact",
            "status",
            "enrollment_date",
        ]
        extra_kwargs = {
            "grade":           {"required": False, "allow_blank": True},
            "guardian_contact":{"required": False, "allow_blank": True},
            "status":          {"required": False},
            "enrollment_date": {"required": False, "allow_null": True},
        }

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------
    def validate_name(self, value):
        value = sanitize_name(value or "")
        if not value:
            raise serializers.ValidationError("Student name is required.")
        return value

    def validate(self, data):
        # Require either a name (to create a Profile) or an existing profile.
        profile = data.get("profile")
        name = data.get("name", "")

        if not profile and not name:
            raise serializers.ValidationError({
                "name": "Provide a student name or an existing profile_id."
            })

        # Default the organization from context / classroom.
        org = get_organization_from_context(self.context)
        classroom = data.get("classroom")
        if not org and classroom:
            org = classroom.organization

        if not org:
            raise serializers.ValidationError({
                "organization": "Organization is required."
            })

        data["_organization"] = org
        return data

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------
    @transaction.atomic
    def create(self, validated_data):
        org = validated_data.pop("_organization")
        name = validated_data.pop("name", "")
        profile = validated_data.pop("profile", None)

        # Link an existing Profile, or create one from `name`.
        if not profile:
            first_name, last_name = split_full_name(name)
            profile = Profile.objects.create(
                first_name=first_name,
                last_name=last_name,
                age=validated_data.get("age"),
                is_active=True,
            )

            # Optionally assign the student role.
            role, _ = Role.objects.get_or_create(role_name="student")
            profile.role = role
            profile.save(update_fields=["role"])

        # Fill in defaults matching the frontend fallbacks.
        validated_data.setdefault("grade", "Grade 1")
        validated_data.setdefault("guardian_name", "Parent")
        validated_data.setdefault("guardian_email", "parent@test.com")
        validated_data.setdefault("status", Student.STATUS_ACTIVE)

        return Student.objects.create(
            profile=profile,
            organization=org,
            **validated_data,
        )


# ======================================================================
# Edit serializer
# ======================================================================

class StudentEditSerializer(serializers.ModelSerializer):
    """
    Update serializer (partial updates supported at the view level).

    Accepts the same frontend aliases as create. Profile fields can be
    updated in the same request via the nested mapping.
    """

    # Frontend aliases -------------------------------------------------
    name = serializers.CharField(
        required=False,
        allow_blank=True,
        write_only=True,
    )
    groupId = serializers.PrimaryKeyRelatedField(
        source="classroom",
        queryset=ClassRoom.objects.all(),
        required=False,
        allow_null=True,
    )
    parentName = serializers.CharField(
        source="guardian_name",
        required=False,
        allow_blank=True,
    )
    parentEmail = serializers.EmailField(
        source="guardian_email",
        required=False,
        allow_blank=True,
    )

    # Profile fields ---------------------------------------------------
    username = serializers.CharField(source="profile.username", required=False)
    first_name = serializers.CharField(source="profile.first_name", required=False, allow_blank=True)
    last_name = serializers.CharField(source="profile.last_name", required=False, allow_blank=True)
    email = serializers.EmailField(source="profile.email", required=False, allow_blank=True)
    contact = serializers.CharField(source="profile.contact", required=False, allow_blank=True)
    address = serializers.CharField(source="profile.address", required=False, allow_blank=True)
    date_of_birth = serializers.DateField(source="profile.date_of_birth", required=False, allow_null=True)
    sex = serializers.CharField(source="profile.sex", required=False, allow_blank=True)
    profile_image = serializers.ImageField(source="profile.profile_image", required=False, allow_null=True)

    class Meta:
        model = Student
        fields = [
            # frontend aliases
            "name",
            "groupId",
            "grade",
            "age",
            "parentName",
            "parentEmail",

            # Profile
            "username",
            "first_name",
            "last_name",
            "email",
            "contact",
            "address",
            "date_of_birth",
            "sex",
            "profile_image",

            # Student
            "guardian_contact",
            "status",
            "enrollment_date",
        ]
        extra_kwargs = {
            "grade":           {"required": False, "allow_blank": True},
            "age":             {"required": False, "allow_null": True},
            "guardian_contact":{"required": False, "allow_blank": True},
            "status":          {"required": False},
            "enrollment_date": {"required": False, "allow_null": True},
        }

    # ------------------------------------------------------------------
    def validate_age(self, value):
        if value is None:
            return value
        if value < 1 or value > 100:
            raise serializers.ValidationError("Age must be between 1 and 100.")
        return value

    def validate_name(self, value):
        return sanitize_name(value or "")

    # ------------------------------------------------------------------
    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop("profile", {})
        name = validated_data.pop("name", None)

        # Split `name` into first/last if provided.
        if name is not None:
            first_name, last_name = split_full_name(name)
            profile_data["first_name"] = first_name
            profile_data["last_name"] = last_name

        # Mirror `age` onto the profile.
        if "age" in validated_data and validated_data["age"] is not None:
            profile_data["age"] = validated_data["age"]

        # Update Student fields.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update Profile fields.
        if profile_data:
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return instance


# ======================================================================
# Registration serializer
# ======================================================================

class StudentRegisterSerializer(serializers.ModelSerializer):
    """
    Full registration: creates a Profile *and* a Student in one call.
    Accepts a nested student_details payload matching addStudent().
    """

    student_details = StudentCreateSerializer(write_only=True, required=True)

    class Meta:
        model = Profile
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "contact",
            "date_of_birth",
            "address",
            "student_details",
        ]
        extra_kwargs = {
            "email": {"required": True},
            "username": {"required": True},
        }

    def validate_student_details(self, value):
        if not value:
            raise serializers.ValidationError("Student details are required.")
        return value

    @transaction.atomic
    def create(self, validated_data):
        student_details = validated_data.pop("student_details")

        org = get_organization_from_context(self.context)
        if not org:
            raise serializers.ValidationError("Organization is required.")

        role, _ = Role.objects.get_or_create(role_name="student")

        profile = Profile.objects.create(
            role=role,
            **validated_data,
        )
        profile.set_unusable_password()
        profile.save()

        # Reuse the create serializer's logic by passing through context.
        student_serializer = StudentCreateSerializer(
            data={
                **student_details,
                "profile_id": profile.pk,
            },
            context={"organization": org},
        )
        student_serializer.is_valid(raise_exception=True)
        return student_serializer.save()
    