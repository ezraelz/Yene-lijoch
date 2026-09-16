from django.db import transaction
from rest_framework import serializers

from .models import Attendance
from students.models import Student
from lessons.models import Lesson


# ======================================================================
# Read
# ======================================================================

class AttendanceSerializer(serializers.ModelSerializer):

    student_name = serializers.SerializerMethodField()
    student_id = serializers.IntegerField(source="student.id", read_only=True)

    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    lesson_date = serializers.DateField(source="lesson.lesson_date", read_only=True)
    class_name = serializers.CharField(source="lesson.classroom.name", read_only=True)

    recorded_by_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Attendance
        fields = [
            "id",

            "lesson",
            "lesson_title",
            "lesson_date",
            "class_name",

            "student",
            "student_id",
            "student_name",

            "status",
            "status_display",
            "note",

            "recorded_by",
            "recorded_by_name",

            "recorded_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "lesson_title",
            "lesson_date",
            "class_name",
            "student_name",
            "status_display",
            "recorded_by_name",
            "recorded_at",
            "updated_at",
        ]

    def get_student_name(self, obj):
        profile = getattr(obj.student, "profile", None)
        if not profile:
            return ""
        return f"{profile.first_name} {profile.last_name}".strip()

    def get_recorded_by_name(self, obj):
        if not obj.recorded_by_id:
            return None
        return obj.recorded_by.full_name


# ======================================================================
# Single create (kept for one-off POSTs)
# ======================================================================

class AttendanceCreateSerializer(serializers.ModelSerializer):

    lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        required=True,
    )
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True,
    )

    class Meta:
        model = Attendance
        fields = ["lesson", "student", "status", "note"]

    def validate(self, data):
        lesson = data.get("lesson")
        student = data.get("student")

        if lesson and student:
            # Use the reverse FK `roster` (source of truth), not the old M2M.
            if not lesson.classroom.roster.filter(id=student.id).exists():
                raise serializers.ValidationError({
                    "student": "This student is not enrolled in the selected class."
                })

        # For POST we reject duplicates — bulk upserts, single does not.
        if Attendance.objects.filter(lesson=lesson, student=student).exists():
            raise serializers.ValidationError({
                "student": "Attendance has already been recorded for this student."
            })

        return data


# ======================================================================
# Bulk upsert — what the AttendanceScreen actually uses
# ======================================================================

class AttendanceRecordInputSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    status = serializers.ChoiceField(choices=Attendance.STATUS_CHOICES)
    note = serializers.CharField(required=False, allow_blank=True, default="")


class AttendanceBulkCreateSerializer(serializers.Serializer):
    """
    Payload:
        {
          "lesson": 42,
          "records": [
            { "student": 10, "status": "present" },
            { "student": 11, "status": "absent", "note": "Sick" }
          ]
        }

    Upserts by (lesson, student). Everything inside one transaction.
    """

    lesson = serializers.PrimaryKeyRelatedField(queryset=Lesson.objects.all())
    records = AttendanceRecordInputSerializer(many=True, allow_empty=False)

    def validate(self, data):
        lesson = data["lesson"]
        records = data["records"]

        # 1. Every student must belong to the lesson's classroom roster.
        roster_ids = set(lesson.classroom.roster.values_list("id", flat=True))
        incoming_ids = [r["student"].id for r in records]

        unknown = set(incoming_ids) - roster_ids
        if unknown:
            raise serializers.ValidationError({
                "records": (
                    f"{len(unknown)} student(s) are not enrolled in "
                    f"{lesson.classroom.name}."
                )
            })

        # 2. No duplicate students in the payload.
        seen = set()
        duplicates = set()
        for sid in incoming_ids:
            if sid in seen:
                duplicates.add(sid)
            seen.add(sid)
        if duplicates:
            raise serializers.ValidationError({
                "records": f"Duplicate student ids: {sorted(duplicates)}"
            })

        return data

    @transaction.atomic
    def create(self, validated_data):
        lesson = validated_data["lesson"]
        records = validated_data["records"]
        request = self.context.get("request")

        teacher = getattr(getattr(request, "user", None), "teacher_profile", None)

        saved = []
        for entry in records:
            record, _ = Attendance.objects.update_or_create(
                lesson=lesson,
                student=entry["student"],
                defaults={
                    "status": entry["status"],
                    "note": entry.get("note", ""),
                    "recorded_by": teacher,
                },
            )
            saved.append(record)

        return saved


# ======================================================================
# Edit
# ======================================================================

class AttendanceEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance
        fields = ["status", "note"]

    def validate_status(self, value):
        valid = {c[0] for c in Attendance.STATUS_CHOICES}
        if value not in valid:
            raise serializers.ValidationError("Invalid attendance status.")
        return value


# ======================================================================
# Summary (plain serializer, not model-bound)
# ======================================================================

class AttendanceSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    recorded = serializers.IntegerField()
    unrecorded = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
    percentage = serializers.FloatField()
    