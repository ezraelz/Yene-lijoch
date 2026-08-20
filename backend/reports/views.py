from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .services.common import get_church_for_user
from .services.dashboard import get_reports_dashboard
from .services.attendance import get_student_attendance_report, get_attendance_summary
from .services.enrollment import get_student_report
from .services.teacher import get_teacher_report
from .services.parent import get_parent_report
from .services.attendance import get_attendance_report
from .services.periods import get_report_period
from .exports.pdf import generate_attendance_pdf
from .exports.csv import generate_attendance_csv
from .exports.excel import generate_attendance_excel

from .serializers import (
    DashboardReportSerializer,
    StudentReportSerializer,
    TeacherReportSerializer,
    ParentReportSerializer,
    AttendanceReportSerializer,
)


class ReportsDashboardAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        report = get_reports_dashboard(
            request.user
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

class AttendanceReportDownloadAPIView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        church = get_church_for_user(
            request.user
        )

        if not church:
            return Response(
                {
                    "detail": (
                        "No church associated "
                        "with user."
                    )
                },
                status=400,
            )

        period = request.query_params.get(
            "period",
            "month",
        )

        file_format = request.query_params.get(
            "format",
            "pdf",
        )

        try:
            start_date, end_date = get_report_period(
                period,
                request.query_params.get(
                    "start_date"
                ),
                request.query_params.get(
                    "end_date"
                ),
            )

        except ValueError as error:

            return Response(
                {"detail": str(error)},
                status=400,
            )

        report = get_attendance_summary(
            church=church,
            start_date=start_date,
            end_date=end_date,
        )

        if file_format == "pdf":
            return generate_attendance_pdf(
                report,
                start_date,
                end_date,
            )

        if file_format == "excel":
            return generate_attendance_excel(
                report,
                start_date,
                end_date,
            )

        if file_format == "csv":
            return generate_attendance_csv(
                report,
                start_date,
                end_date,
            )

        return Response(
            {
                "detail": (
                    "Supported formats: "
                    "pdf, excel, csv"
                )
            },
            status=400,
        )

        