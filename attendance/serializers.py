from rest_framework import serializers

from .models import Attendance
from students.models import Student
from lessons.models import Lesson


class AttendanceSerializer(serializers.ModelSerializer):

    student_name = serializers.SerializerMethodField()

    lesson_title = serializers.CharField(
        source="lesson.title",
        read_only=True
    )

    lesson_date = serializers.DateField(
        source="lesson.lesson_date",
        read_only=True
    )

    class_name = serializers.CharField(
        source="lesson.classroom.name",
        read_only=True
    )

    class Meta:
        model = Attendance

        fields = [
            "id",

            "lesson",
            "lesson_title",
            "lesson_date",
            "class_name",

            "student",
            "student_name",

            "status",
            "note",

            "recorded_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "lesson_title",
            "lesson_date",
            "class_name",
            "student_name",
            "recorded_at",
            "updated_at",
        ]

    def get_student_name(self, obj):

        return (
            f"{obj.student.profile.first_name} "
            f"{obj.student.profile.last_name}"
        )

class AttendanceCreateSerializer(serializers.ModelSerializer):

    lesson = serializers.PrimaryKeyRelatedField(
        queryset=Lesson.objects.all(),
        required=True
    )

    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        required=True
    )

    class Meta:
        model = Attendance

        fields = [
            "lesson",
            "student",
            "status",
            "note",
        ]

        extra_kwargs = {
            "lesson": {
                "required": True
            },
            "student": {
                "required": True
            },
        }

    def validate(self, data):

        lesson = data.get("lesson")
        student = data.get("student")

        # Make sure student belongs to the class
        if lesson and student:

            if not lesson.classroom.students.filter(
                id=student.id
            ).exists():

                raise serializers.ValidationError({
                    "student":
                        "This student is not enrolled in the selected class."
                })

        # Prevent duplicate attendance
        if Attendance.objects.filter(
            lesson=lesson,
            student=student
        ).exists():

            raise serializers.ValidationError({
                "student":
                    "Attendance has already been recorded for this student."
            })

        return data

class AttendanceEditSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attendance

        fields = [
            "status",
            "note",
    ]

    def validate_status(self, value):

        valid_statuses = [
            "present",
            "absent",
            "late",
            "excused",
        ]

        if value not in valid_statuses:
            raise serializers.ValidationError(
                "Invalid attendance status."
            )

        return value

