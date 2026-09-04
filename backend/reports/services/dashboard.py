from teachers.models import Teacher
from students.models import Student
from parents.models import Parent
from .common import get_organization_for_user
from django.utils import timezone
from .health import get_health_report
from .enrollment import get_enrollment_report
from .attendance import get_attendance_summary
from .curriculum import get_curriculum_report
from .teacher import get_teacher_performance_report

def get_dashboard_report(user):
    """
    Generate a summary report for the authenticated user's church.
    """

    organization = get_organization_for_user(user)

    if not organization:
        return None

    students = Student.objects.filter(organization=organization)
    teachers = Teacher.objects.filter(organization=organization)
    parents = Parent.objects.filter(organization=organization)

    return {
        "organization": {
            "id": organization.id,
            "name": organization.name,
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


def get_reports_dashboard(user):

    if not get_organization_for_user(user):
        return None

    today = timezone.now().date()

    # Current month
    month_start = today.replace(day=1)

    # Q3 example
    q3_start = today.replace(
        month=7,
        day=1
    )

    q3_end = today.replace(
        month=9,
        day=30
    )

    return {
        "health": get_health_report(user),

        "enrollment": get_enrollment_report(
            user,
            year=today.year,
            month=today.month
        ),

        "attendance": {
            "period": "Q3 2026",
            **get_attendance_summary(
                user,
                start_date=q3_start,
                end_date=q3_end
            )
        },

        "curriculum": {
            "period": today.strftime("%B %Y"),
            **get_curriculum_report(
                user,
                start_date=month_start,
                end_date=today
            )
        },

        "teachers": {
            "period": today.strftime("%B %Y"),
            **get_teacher_performance_report(
                user,
                start_date=month_start,
                end_date=today
            )
        },
    }

