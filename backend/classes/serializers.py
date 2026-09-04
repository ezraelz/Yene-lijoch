from rest_framework import serializers

from .models import ClassRoom
from teachers.models import Teacher
from students.models import Student


class ClassRoomSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    students_count = serializers.SerializerMethodField()

    class Meta:
        model = ClassRoom

        fields = [
            "id",

            "organization",

            "name",
            "description",
            "age_group",

            "teacher",
            "teacher_name",

            "students",
            "students_count",

            "room",
            "status",

            "start_date",
            "end_date",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "teacher_name",
            "students_count",
            "created_at",
            "updated_at",
        ]

    def get_teacher_name(self, obj):
        if not obj.teacher:
            return ""
        return (
            f"{obj.teacher.profile.first_name} "
            f"{obj.teacher.profile.last_name}"
        )

    def get_students_count(self, obj):
        return obj.students.count()

class ClassRoomCreateSerializer(serializers.ModelSerializer):

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True
    )

    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = ClassRoom

        fields = [
            "organization",
            "name",
            "age_group",
            "description",
            "teacher",
            "students",
            "room",
            "status",
            "start_date",
            "end_date",
        ]

        extra_kwargs = {
            "organization": {
                "required": True
            },
            "name": {
                "required": True
            },
        }

    def validate(self, data):

        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if start_date and end_date:

            if end_date < start_date:
                raise serializers.ValidationError({
                    "end_date": "End date cannot be before start date."
                })

        return data

class ClassRoomEditSerializer(serializers.ModelSerializer):

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True
    )

    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = ClassRoom

        fields = [
            "organization",
            "name",
            "age_group",
            "description",
            "teacher",
            "students",
            "room",
            "status",
            "start_date",
            "end_date",
        ]

    def validate(self, data):

        start_date = data.get(
            "start_date",
            self.instance.start_date
            if self.instance else None
        )

        end_date = data.get(
            "end_date",
            self.instance.end_date
            if self.instance else None
        )

        if start_date and end_date:

            if end_date < start_date:
                raise serializers.ValidationError({
                    "end_date": "End date cannot be before start date."
                })

        return data

