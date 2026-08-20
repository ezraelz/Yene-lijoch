from students.models import Student
from .common import get_church_for_user
from django.db.models import Count, Q
from django.utils import timezone


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

def get_enrollment_report(user, year=None, month=None):

    church = get_church_for_user(user)

    if not church:
        return None

    students = Student.objects.filter(
        church=church
    )

    today = timezone.now().date()

    if year is None:
        year = today.year

    if month is None:
        month = today.month

    monthly_students = students.filter(
        enrollment_date__year=year,
        enrollment_date__month=month
    )

    return {
        "period": f"{year}-{int(month):02d}",

        "new_students": monthly_students.count(),

        "active_students": students.filter(
            status=Student.Status.ACTIVE
        ).count(),

        "graduated_students": students.filter(
            status=Student.Status.GRADUATED
        ).count(),

        "total_students": students.count(),
    }


