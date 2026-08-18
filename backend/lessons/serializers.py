from rest_framework import serializers
from .models import Lesson
from classes.models import ClassRoom
from teachers.models import Teacher


class LessonSerializer(serializers.ModelSerializer):

    classroom_name = serializers.CharField(
        source="classroom.name",
        read_only=True
    )

    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = Lesson

        fields = [
            "id",

            "classroom",
            "classroom_name",

            "teacher",
            "teacher_name",

            "title",
            "description",

            "lesson_date",
            "start_time",
            "end_time",

            "content",
            "objectives",

            "status",

            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "classroom_name",
            "teacher_name",
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

class LessonCreateSerializer(serializers.ModelSerializer):

    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        required=True
    )

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Lesson

        fields = [
            "classroom",
            "teacher",

            "title",
            "description",

            "lesson_date",
            "start_time",
            "end_time",

            "content",
            "objectives",

            "status",
        ]

        extra_kwargs = {
            "classroom": {
                "required": True
            },

            "title": {
                "required": True
            },

            "lesson_date": {
                "required": True
            },
        }

    def validate(self, data):
        classroom = data.get("classroom")
        teacher = data.get("teacher")

        start_time = data.get("start_time")
        end_time = data.get("end_time")

        if teacher and classroom:

            if classroom.teacher_id != teacher.id:
                raise serializers.ValidationError({
                    "teacher":
                        "This teacher is not assigned to the selected class."
                })

        if end_time and not start_time:
            raise serializers.ValidationError({
                "start_time":
                    "Start time is required when end time is provided."
            })

        if start_time and end_time:

            if end_time <= start_time:
                raise serializers.ValidationError({
                    "end_time":
                        "End time must be after start time."
                })

        return data

class LessonEditSerializer(serializers.ModelSerializer):

    classroom = serializers.PrimaryKeyRelatedField(
        queryset=ClassRoom.objects.all(),
        required=False
    )

    teacher = serializers.PrimaryKeyRelatedField(
        queryset=Teacher.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Lesson

        fields = [
            "classroom",
            "teacher",

            "title",
            "description",

            "lesson_date",
            "start_time",
            "end_time",

            "content",
            "objectives",

            "status",
        ]

    def validate(self, data):

        start_time = data.get(
            "start_time",
            self.instance.start_time
            if self.instance
            else None
        )

        end_time = data.get(
            "end_time",
            self.instance.end_time
            if self.instance
            else None
        )

        if start_time and end_time:

            if end_time <= start_time:
                raise serializers.ValidationError({
                    "end_time":
                        "End time must be after start time."
                })

        return data

