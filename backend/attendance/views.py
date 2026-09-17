from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from students.models import Student
from .models import Attendance
from .serializers import (
    AttendanceSerializer,
    AttendanceCreateSerializer,
    AttendanceBulkCreateSerializer,
    AttendanceEditSerializer,
    AttendanceSummarySerializer,
)
from lessons.models import Lesson
from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
    get_user_teacher
)

# ======================================================================
# Scoping helpers (same pattern as everywhere else)
# ======================================================================

def scope_attendance(qs, user):
    """
    Superuser → all.
    Teacher   → only records for lessons in their own classes.
    Admin     → only records for lessons in their org.
    """
    if is_superuser(user):
        return qs

    teacher = get_user_teacher(user)
    if teacher:
        return qs.filter(lesson__classroom__teacher=teacher)

    org = get_user_organization(user)
    if not org:
        return qs.none()
    return qs.filter(lesson__classroom__organization=org)


def scope_lessons(qs, user):
    """Same idea, for Lesson querysets."""
    if is_superuser(user):
        return qs

    teacher = get_user_teacher(user)
    if teacher:
        return qs.filter(classroom__teacher=teacher)

    org = get_user_organization(user)
    if not org:
        return qs.none()
    return qs.filter(classroom__organization=org)


# ======================================================================
# List + single create
# ======================================================================

class AttendanceListCreateAPIView(APIView):
    """
    GET  /attendance/?lesson=<id>       list for a lesson
    GET  /attendance/?student=<id>      list for a student
    POST /attendance/                   single create
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Attendance.objects.select_related(
            "student__profile",
            "lesson__classroom",
            "recorded_by__profile",
        )
        qs = scope_attendance(qs, request.user)

        lesson_id = request.query_params.get("lesson")
        if lesson_id:
            qs = qs.filter(lesson_id=lesson_id)

        student_id = request.query_params.get("student")
        if student_id:
            qs = qs.filter(student_id=student_id)

        return Response(AttendanceSerializer(qs, many=True).data)

    def post(self, request):
        if not (is_admin(request.user) or get_user_teacher(request.user)):
            raise PermissionDenied("Only teachers and admins can record attendance.")

        serializer = AttendanceCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        record = serializer.save(recorded_by=get_user_teacher(request.user))
        return Response(
            AttendanceSerializer(record).data,
            status=status.HTTP_201_CREATED,
        )


# ======================================================================
# Bulk upsert — AttendanceScreen's save button
# ======================================================================

class AttendanceBulkCreateAPIView(APIView):
    """POST /attendance/bulk/"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not (is_admin(request.user) or get_user_teacher(request.user)):
            raise PermissionDenied("Only teachers and admins can record attendance.")

        serializer = AttendanceBulkCreateSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        records = serializer.save()

        return Response(
            AttendanceSerializer(records, many=True).data,
            status=status.HTTP_201_CREATED,
        )


# ======================================================================
# Summary — TeacherHome's attendance card
# ======================================================================

class AttendanceSummaryAPIView(APIView):
    """GET /attendance/summary/?lesson=<id> OR ?student=<id>"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        lesson_id = request.query_params.get("lesson")
        student_id = request.query_params.get("student")

        # ----- Case 1: summary for one lesson ------------------------
        if lesson_id:
            lesson = get_object_or_404(
                scope_lessons(Lesson.objects.all(), request.user),
                pk=lesson_id,
            )
            total = lesson.classroom.roster.count()
            records = Attendance.objects.filter(lesson=lesson)
            present = records.filter(status=Attendance.STATUS_PRESENT).count()
            absent = records.filter(status=Attendance.STATUS_ABSENT).count()
            late = records.filter(status=Attendance.STATUS_LATE).count()
            excused = records.filter(status=Attendance.STATUS_EXCUSED).count()

            data = {
                "total": total,
                "recorded": records.count(),
                "unrecorded": max(0, total - records.count()),
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
                "percentage": round((present / total) * 100, 1) if total else 0,
            }
            return Response(AttendanceSummarySerializer(data).data)

        # ----- Case 2: summary for one student (all lessons) ---------
        if student_id:
            # Access control — parents only see their own child.
            student = get_object_or_404(Student, pk=student_id)
            user = request.user

            if not is_superuser(user) and not is_admin(user):
                parent = getattr(user, "parent_profile", None)
                owns = False
                if parent:
                    owns = Student.objects.filter(
                        pk=student.pk,
                        parents=parent,       # adjust to your schema
                    ).exists()
                teacher = get_user_teacher(user)
                if teacher:
                    owns = owns or (
                        student.classroom
                        and student.classroom.teacher_id == teacher.id
                    )
                if not owns:
                    raise PermissionDenied(
                        "You do not have access to this student's attendance."
                    )

            records = Attendance.objects.filter(student=student)
            total = records.count()
            present = records.filter(status=Attendance.STATUS_PRESENT).count()
            absent = records.filter(status=Attendance.STATUS_ABSENT).count()
            late = records.filter(status=Attendance.STATUS_LATE).count()
            excused = records.filter(status=Attendance.STATUS_EXCUSED).count()

            data = {
                "total": total,
                "recorded": total,
                "unrecorded": 0,
                "present": present,
                "absent": absent,
                "late": late,
                "excused": excused,
                "percentage": round((present / total) * 100, 1) if total else 0,
            }
            return Response(AttendanceSummarySerializer(data).data)

        return Response(
            {"detail": "Either lesson or student query param is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# ======================================================================
# Detail
# ======================================================================

class AttendanceDetailAPIView(APIView):
    """
    GET    /attendance/<id>/
    PATCH  /attendance/<id>/
    DELETE /attendance/<id>/
    """

    permission_classes = [IsAuthenticated]

    def get_object(self, request, pk):
        qs = scope_attendance(Attendance.objects.all(), request.user)
        return get_object_or_404(qs, pk=pk)

    def get(self, request, pk):
        return Response(AttendanceSerializer(self.get_object(request, pk)).data)

    def patch(self, request, pk):
        if not (is_admin(request.user) or get_user_teacher(request.user)):
            raise PermissionDenied("You do not have permission to edit attendance.")

        record = self.get_object(request, pk)
        serializer = AttendanceEditSerializer(record, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        record = serializer.save()
        return Response(AttendanceSerializer(record).data)

    def delete(self, request, pk):
        if not (is_admin(request.user) or get_user_teacher(request.user)):
            raise PermissionDenied("You do not have permission to delete attendance.")

        self.get_object(request, pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    