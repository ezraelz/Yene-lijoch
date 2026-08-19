from django.db.models import Count
from django.db.models import Count, Q
from django.utils import timezone

from attendance.models import Attendance
from churches.models import Church
from teachers.models import Teacher
from students.models import Student
from parents.models import Parent


def get_church_for_user(user):
    """
    Return the church associated with the authenticated user.
    """

    if not hasattr(user, "profile"):
        return None

    return user.profile.church

def get_dashboard_report(user):
    """
    Generate a summary report for the authenticated user's church.
    """

    church = get_church_for_user(user)

    if not church:
        return None

    students = Student.objects.filter(church=church)
    teachers = Teacher.objects.filter(church=church)
    parents = Parent.objects.filter(church=church)

    return {
        "church": {
            "id": church.id,
            "name": church.name,
        },

        "students": {
            "total": students.count(),
            "active": students.filter(
                status=Student.Status.ACTIVE
            ).count(),
            "graduated": students.filter(
                status=Student.Status.GRADUATED
            ).count(),
        },

        "teachers": {
            "total": teachers.count(),
        },

        "parents": {
            "total": parents.count(),
        },
    }

def get_student_report(user, start_date=None, end_date=None):

    church = get_church_for_user(user)

    if not church:
        return None

    students = Student.objects.filter(
        church=church
    )

    if start_date:
        students = students.filter(
            enrollment_date__gte=start_date
        )

    if end_date:
        students = students.filter(
            enrollment_date__lte=end_date
        )

    return {
        "total": students.count(),

        "active": students.filter(
            status=Student.Status.ACTIVE
        ).count(),

        "graduated": students.filter(
            status=Student.Status.GRADUATED
        ).count(),

        "students": list(
            students.select_related(
                "profile"
            ).values(
                "id",
                "profile__first_name",
                "profile__last_name",
                "guardian_name",
                "guardian_contact",
                "status",
                "enrollment_date",
            )
        ),
    }

def get_teacher_report(user):
    """
    Generate a teacher summary report.
    """

    church = get_church_for_user(user)

    if not church:
        return None

    teachers = Teacher.objects.filter(
        church=church
    ).prefetch_related(
        "subject",
        "profile"
    )

    teacher_data = []

    for teacher in teachers:

        subjects = list(
            teacher.subject.values(
                "id",
                "name"
            )
        )

        teacher_data.append({
            "id": teacher.id,
            "first_name": teacher.profile.first_name,
            "last_name": teacher.profile.last_name,
            "employment_date": teacher.employment_date,
            "available_days": teacher.available_days,
            "subjects": subjects,
        })

    return {
        "total": teachers.count(),
        "teachers": teacher_data,
    }

def get_parent_report(user):
    """
    Generate a parent summary report.
    """

    church = get_church_for_user(user)

    if not church:
        return None

    parents = Parent.objects.filter(
        church=church
    ).prefetch_related(
        "student",
        "profile"
    )

    parent_data = []

    for parent in parents:

        students = list(
            parent.student.values(
                "id",
                "guardian_name",
                "status"
            )
        )

        parent_data.append({
            "id": parent.id,
            "first_name": parent.profile.first_name,
            "last_name": parent.profile.last_name,
            "relationship": parent.relationship,
            "students": students,
        })

    return {
        "total": parents.count(),
        "parents": parent_data,
    }

def get_student_status_report(user):
    church = get_church_for_user(user)

    if not church:
        return None

    students = Student.objects.filter(
        church=church
    )

    return {
        "total": students.count(),

        "active": students.filter(
            status=Student.Status.ACTIVE
        ).count(),

        "graduated": students.filter(
            status=Student.Status.GRADUATED
        ).count(),

        "by_status": list(
            students.values("status").annotate(
                count=Count("id")
            )
        ),
    }

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

    church = get_church_for_user(user)

    if not church:
        return None

    attendance = Attendance.objects.filter(
        student__church=church
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

    church = get_church_for_user(user)

    if not church:
        return None

    attendance = Attendance.objects.filter(
        student__church=church
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
        church=church
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
