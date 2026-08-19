from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import (
    get_dashboard_report,
    get_student_report,
    get_teacher_report,
    get_parent_report,
    get_attendance_report,
    get_student_attendance_report,
)

from .serializers import (
    DashboardReportSerializer,
    StudentReportSerializer,
    TeacherReportSerializer,
    ParentReportSerializer,
    AttendanceReportSerializer,
)


class DashboardReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        report = get_dashboard_report(request.user)

        if report is None:
            return Response({
                "detail": "Your account is not associated with a church."
            }, status=400)

        serializer = DashboardReportSerializer(report)

        return Response(serializer.data)


class StudentReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        report = get_student_report(request.user)

        if report is None:
            return Response({
                "detail": "Your account is not associated with a church."
            }, status=400)

        serializer = StudentReportSerializer(report)

        return Response(serializer.data)


class TeacherReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        report = get_teacher_report(request.user)

        if report is None:
            return Response({
                "detail": "Your account is not associated with a church."
            }, status=400)

        serializer = TeacherReportSerializer(report)

        return Response(serializer.data)


class ParentReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        report = get_parent_report(request.user)

        if report is None:
            return Response({
                "detail": "Your account is not associated with a church."
            }, status=400)

        serializer = ParentReportSerializer(report)

        return Response(serializer.data)


class AttendanceReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        start_date = request.query_params.get(
            "start_date"
        )

        end_date = request.query_params.get(
            "end_date"
        )

        student_id = request.query_params.get(
            "student_id"
        )

        lesson_id = request.query_params.get(
            "lesson_id"
        )

        report = get_attendance_report(
            request.user,
            start_date=start_date,
            end_date=end_date,
            student_id=student_id,
            lesson_id=lesson_id,
        )

        if report is None:
            return Response(
                {
                    "detail": (
                        "Your account is not associated "
                        "with a church."
                    )
                },
                status=400
            )

        serializer = AttendanceReportSerializer(
            report
        )

        return Response(serializer.data)

class StudentAttendanceReportAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        start_date = request.query_params.get(
            "start_date"
        )

        end_date = request.query_params.get(
            "end_date"
        )

        report = get_student_attendance_report(
            request.user,
            start_date=start_date,
            end_date=end_date,
        )

        if report is None:
            return Response(
                {
                    "detail": (
                        "Your account is not associated "
                        "with a church."
                    )
                },
                status=400
            )

        return Response(report)
        