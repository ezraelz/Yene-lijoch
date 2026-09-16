from django.db import transaction
from rest_framework import serializers

from .models import ClassRoom
from teachers.models import Teacher
from students.models import Student
from students.serializers import StudentSerializer


# ======================================================================
# Shared helper
# ======================================================================

def _teacher_full_name(teacher):
    if not teacher:
        return ""
    profile = getattr(teacher, "profile", None)
    if not profile:
        return str(teacher)
    first = getattr(profile, "first_name", "") or ""
    last = getattr(profile, "last_name", "") or ""
    return f"{first} {last}".strip()


def _resolve_organization(context, data=None):
    if data and data.get("organization"):
        return data["organization"]
    return context.get("organization")


# ======================================================================
# Read
# ======================================================================

class ClassRoomSerializer(serializers.ModelSerializer):
    """
    Read serializer matching the frontend's Group shape:

        { id, name, teacherName, grade, student_count, roster, status }
    """

    organization_name = serializers.CharField(
        source="organization.name",
        read_only=True,
        allow_null=True,
    )

    # camelCase aliases the frontend reads directly.
    teacherName = serializers.SerializerMethodField()
    roster = serializers.SerializerMethodField()

    class Meta:
        model = ClassRoom
        fields = [
            "id",

            "organization",
            "organization_name",

            # Frontend core
            "name",
            "teacherName",
            "grade",
            "student_count",
            "roster",

            # Native
            "description",
            "age_group",
            "teacher",
            "status",
            "start_date",
            "end_date",

            "created_at",
            "updated_at",
        ]
        read_only_fields = fields

    def get_teacherName(self, obj):
        if obj.teacher_id:
            full = _teacher_full_name(obj.teacher)
            if full:
                return full
        return obj.teacher_name or ""

    def get_roster(self, obj):
        students = getattr(obj, "roster", None)
        qs = students.all() if students is not None else Student.objects.none()
        return StudentSerializer(qs, many=True, context=self.context).data


# ======================================================================
# Create
# ======================================================================

class ClassRoomCreateSerializer(serializers.ModelSerializer):
    """
    Accepts the frontend's group-creation payload, including nested
    students created atomically with the group.
    """

    teacherName = serializers.CharField(
        source="teacher_name",
        required=False,
        allow_blank=True,
    )
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True,
    )
    students = StudentSerializer(many=True, required=False)

    class Meta:
        model = ClassRoom
        fields = [
            "name",
            "description",
            "age_group",
            "grade",

            "teacherName",
            "teacher",

            "students",

            "status",
            "start_date",
            "end_date",
        ]
        extra_kwargs = {
            "name":       {"required": True},
            "grade":      {"required": False, "allow_blank": True},
            "age_group":  {"required": False, "allow_blank": True},
            "description":{"required": False, "allow_blank": True},
            "status":     {"required": False},
            "start_date": {"required": False, "allow_null": True},
            "end_date":   {"required": False, "allow_null": True},
        }

    def validate_name(self, value):
        value = (value or "").strip()
        if not value:
            raise serializers.ValidationError("Group name is required.")
        return value

    def validate(self, data):
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        org = _resolve_organization(self.context, data)
        if not org:
            raise serializers.ValidationError({
                "organization": "Organization is required."
            })

        name = data.get("name")
        if name:
            if ClassRoom.objects.filter(organization=org, name__iexact=name).exists():
                raise serializers.ValidationError({
                    "name": f"A group named '{name}' already exists."
                })

        return data

    @transaction.atomic
    def create(self, validated_data):
        students_data = validated_data.pop("students", [])

        org = _resolve_organization(self.context, validated_data)
        created_by = self.context.get("created_by")

        classroom = ClassRoom.objects.create(
            organization=org,
            created_by=created_by,
            **validated_data,
        )

        for entry in students_data:
            Student.objects.create(
                organization=org,
                classroom=classroom,
                name=entry.get("name", "").strip(),
                grade=entry.get("grade") or "Grade 1",
                age=entry.get("age") or None,
                parent_name=entry.get("parent_name") or "Parent",
                parent_email=entry.get("parent_email") or "parent@test.com",
            )

        return classroom


# ======================================================================
# Edit
# ======================================================================

class ClassRoomEditSerializer(serializers.ModelSerializer):
    teacherName = serializers.CharField(
        source="teacher_name",
        required=False,
        allow_blank=True,
    )
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True,
    )
    students = StudentSerializer(many=True, required=False)

    class Meta:
        model = ClassRoom
        fields = [
            "organization",
            "name",
            "description",
            "age_group",
            "grade",

            "teacherName",
            "teacher",

            "students",

            "status",
            "start_date",
            "end_date",
        ]
        extra_kwargs = {
            "organization": {"required": False},
            "name":         {"required": False},
            "grade":        {"required": False, "allow_blank": True},
            "age_group":    {"required": False, "allow_blank": True},
            "description":  {"required": False, "allow_blank": True},
            "status":       {"required": False},
            "start_date":   {"required": False, "allow_null": True},
            "end_date":     {"required": False, "allow_null": True},
        }

    def validate(self, data):
        instance = self.instance

        start_date = data.get("start_date", getattr(instance, "start_date", None))
        end_date = data.get("end_date", getattr(instance, "end_date", None))
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError({
                "end_date": "End date cannot be before start date."
            })

        name = data.get("name", getattr(instance, "name", None))
        org = data.get("organization", getattr(instance, "organization", None))
        if name and org:
            qs = ClassRoom.objects.filter(
                organization=org, name__iexact=name
            ).exclude(pk=instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    "name": f"A group named '{name}' already exists."
                })

        return data

    @transaction.atomic
    def update(self, instance, validated_data):
        students_data = validated_data.pop("students", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if students_data is not None:
            self._sync_roster(instance, students_data)

        return instance

    def _sync_roster(self, classroom, students_data):
        incoming_ids = set()
        to_create = []

        for entry in students_data:
            sid = entry.get("id")
            if sid:
                incoming_ids.add(sid)
            else:
                to_create.append(entry)

        # Detach students not in the payload.
        classroom.roster.exclude(id__in=incoming_ids).update(classroom=None)

        # Update existing.
        for entry in students_data:
            sid = entry.get("id")
            if not sid:
                continue
            Student.objects.filter(pk=sid).update(
                classroom=classroom,
                name=entry.get("name", ""),
                grade=entry.get("grade") or "Grade 1",
                age=entry.get("age") or None,
                parent_name=entry.get("parent_name") or "Parent",
                parent_email=entry.get("parent_email") or "parent@test.com",
            )

        # Create new.
        for entry in to_create:
            Student.objects.create(
                organization=classroom.organization,
                classroom=classroom,
                name=entry.get("name", "").strip(),
                grade=entry.get("grade") or "Grade 1",
                age=entry.get("age") or None,
                parent_name=entry.get("parent_name") or "Parent",
                parent_email=entry.get("parent_email") or "parent@test.com",
            )
