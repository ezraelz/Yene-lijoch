from django.utils import timezone
from lessons.models import Lesson
from attendance.models import Attendance
from organizations.models import Organization
from teachers.models import Teacher
from students.models import Student
from parents.models import Parent
from classes.models import ClassRoom
from .common import get_organization_for_user

def get_curriculum_report(
    user,
    start_date=None,
    end_date=None,
):
    organization = get_organization_for_user(user)

    if not organization:
        return None

    lessons = Lesson.objects.filter(
        classroom__organization=organization
    )

    if start_date:
        lessons = lessons.filter(
            lesson_date__gte=start_date
        )

    if end_date:
        lessons = lessons.filter(
            lesson_date__lte=end_date
        )

    total = lessons.count()

    planned = lessons.filter(
        status="planned"
    ).count()

    ongoing = lessons.filter(
        status="ongoing"
    ).count()

    completed = lessons.filter(
        status="completed"
    ).count()

    cancelled = lessons.filter(
        status="cancelled"
    ).count()

    completion_percentage = 0

    if total:
        # Cancelled lessons shouldn't count as
        # part of the curriculum completion denominator.
        active_lessons = total - cancelled

        if active_lessons > 0:
            completion_percentage = round(
                (completed / active_lessons) * 100,
                2
            )

    return {
        "total_lessons": total,
        "planned": planned,
        "ongoing": ongoing,
        "completed": completed,
        "cancelled": cancelled,
        "completion_percentage": completion_percentage,
    }

