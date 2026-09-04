from rest_framework import serializers


class StudentReportSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    active = serializers.IntegerField()
    graduated = serializers.IntegerField()
    students = serializers.ListField()


class TeacherReportSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    teachers = serializers.ListField()


class ParentReportSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    parents = serializers.ListField()


class DashboardReportSerializer(serializers.Serializer):
    organization = serializers.DictField()
    students = serializers.DictField()
    teachers = serializers.DictField()
    parents = serializers.DictField()

class AttendanceSummarySerializer(serializers.Serializer):
    total = serializers.IntegerField()
    present = serializers.IntegerField()
    absent = serializers.IntegerField()
    late = serializers.IntegerField()
    excused = serializers.IntegerField()
    attendance_percentage = serializers.FloatField()


class AttendanceReportSerializer(serializers.Serializer):
    summary = AttendanceSummarySerializer()
    records = serializers.ListField()
    