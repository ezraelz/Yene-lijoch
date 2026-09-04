from django.db.models import Count, Q
from django.utils import timezone
from lessons.models import Lesson
from attendance.models import Attendance
from organizations.models import Organization
from teachers.models import Teacher
from students.models import Student
from parents.models import Parent
from classes.models import ClassRoom
from .common import get_organization_for_user

def get_attendance_report(
    user,
    start_date=None,
    end_date=None,
    student_id=None,
    lesson_id=None,
):
    """
    Generate an attendance report for the authenticated user's church.
    """

    organization = get_organization_for_user(user)

    if not organization:
        return None

    attendance = Attendance.objects.filter(
        student__organization=organization
    ).select_related(
        "student__profile",
        "lesson",
    )

    # Date filtering based on when attendance was recorded
    if start_date:
        attendance = attendance.filter(
            recorded_at__date__gte=start_date
        )

    if end_date:
        attendance = attendance.filter(
            recorded_at__date__lte=end_date
        )

    # Filter by student
    if student_id:
        attendance = attendance.filter(
            student_id=student_id
        )

    # Filter by lesson
    if lesson_id:
        attendance = attendance.filter(
            lesson_id=lesson_id
        )

    total = attendance.count()

    present = attendance.filter(
        status="present"
    ).count()

    absent = attendance.filter(
        status="absent"
    ).count()

    late = attendance.filter(
        status="late"
    ).count()

    excused = attendance.filter(
        status="excused"
    ).count()

    attendance_percentage = 0

    if total > 0:
        attendance_percentage = round(
            ((present + late) / total) * 100,
            2
        )

    records = []

    for record in attendance:

        records.append({
            "id": record.id,

            "student": {
                "id": record.student.id,
                "first_name": record.student.profile.first_name,
                "last_name": record.student.profile.last_name,
            },

            "lesson": {
                "id": record.lesson.id,
                "title": record.lesson.title,
            },

            "status": record.status,

            "note": record.note,

            "recorded_at": record.recorded_at,

            "updated_at": record.updated_at,
        })

    return {
        "summary": {
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "attendance_percentage": attendance_percentage,
        },

        "records": records,
    }


def get_student_attendance_report(
    user,
    start_date=None,
    end_date=None,
):
    """
    Generate attendance statistics for every student
    in the authenticated user's church.
    """

    organization = get_organization_for_user(user)

    if not organization:
        return None

    attendance = Attendance.objects.filter(
        student__organization=organization
    )

    if start_date:
        attendance = attendance.filter(
            recorded_at__date__gte=start_date
        )

    if end_date:
        attendance = attendance.filter(
            recorded_at__date__lte=end_date
        )

    students = Student.objects.filter(
        organization=organization
    ).select_related(
        "profile"
    )

    results = []

    for student in students:

        student_attendance = attendance.filter(
            student=student
        )

        total = student_attendance.count()

        present = student_attendance.filter(
            status="present"
        ).count()

        absent = student_attendance.filter(
            status="absent"
        ).count()

        late = student_attendance.filter(
            status="late"
        ).count()

        excused = student_attendance.filter(
            status="excused"
        ).count()

        percentage = 0

        if total > 0:
            percentage = round(
                ((present + late) / total) * 100,
                2
            )

        results.append({
            "student": {
                "id": student.id,
                "first_name": student.profile.first_name,
                "last_name": student.profile.last_name,
            },
            "total": total,
            "present": present,
            "absent": absent,
            "late": late,
            "excused": excused,
            "attendance_percentage": percentage,
        })

    return {
        "students": results
    }


def get_attendance_summary(
    user,
    start_date=None,
    end_date=None
):

    organization = get_organization_for_user(user)

    if not organization:
        return None

    attendance = Attendance.objects.filter(
        student__organization=organization
    )

    if start_date:
        attendance = attendance.filter(
            lesson__lesson_date__gte=start_date
        )

    if end_date:
        attendance = attendance.filter(
            lesson__lesson_date__lte=end_date
        )

    total = attendance.count()

    present = attendance.filter(
        status="present"
    ).count()

    absent = attendance.filter(
        status="absent"
    ).count()

    late = attendance.filter(
        status="late"
    ).count()

    excused = attendance.filter(
        status="excused"
    ).count()

    attendance_percentage = 0

    if total:
        attendance_percentage = round(
            ((present + late) / total) * 100,
            2
        )

    return {
        "total_records": total,
        "present": present,
        "absent": absent,
        "late": late,
        "excused": excused,
        "attendance_percentage": attendance_percentage,
    }

