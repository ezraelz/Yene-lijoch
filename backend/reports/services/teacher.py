from .common import get_church_for_user
from teachers.models import Teacher
from lessons.models import Lesson
from attendance.models import Attendance

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


def get_teacher_performance_report(
    user,
    start_date=None,
    end_date=None,
):
    church = get_church_for_user(user)

    if not church:
        return None

    teachers = Teacher.objects.filter(
        church=church
    ).select_related(
        "profile"
    ).prefetch_related(
        "classes"
    )

    results = []

    for teacher in teachers:

        lessons = Lesson.objects.filter(
            teacher=teacher,
            classroom__church=church
        )

        if start_date:
            lessons = lessons.filter(
                lesson_date__gte=start_date
            )

        if end_date:
            lessons = lessons.filter(
                lesson_date__lte=end_date
            )

        total_lessons = lessons.count()

        completed_lessons = lessons.filter(
            status="completed"
        ).count()

        cancelled_lessons = lessons.filter(
            status="cancelled"
        ).count()

        effective_lessons = (
            total_lessons - cancelled_lessons
        )

        lesson_completion_rate = 0

        if effective_lessons > 0:
            lesson_completion_rate = round(
                (
                    completed_lessons /
                    effective_lessons
                ) * 100,
                2
            )

        attendance = Attendance.objects.filter(
            lesson__teacher=teacher,
            lesson__classroom__church=church
        )

        if start_date:
            attendance = attendance.filter(
                lesson__lesson_date__gte=start_date
            )

        if end_date:
            attendance = attendance.filter(
                lesson__lesson_date__lte=end_date
            )

        total_attendance = attendance.count()

        present = attendance.filter(
            status="present"
        ).count()

        late = attendance.filter(
            status="late"
        ).count()

        attendance_rate = 0

        if total_attendance:
            attendance_rate = round(
                (
                    (present + late) /
                    total_attendance
                ) * 100,
                2
            )

        performance_score = round(
            (
                lesson_completion_rate * 0.5
                +
                attendance_rate * 0.5
            ),
            2
        )

        results.append({
            "teacher": {
                "id": teacher.id,
                "first_name": teacher.profile.first_name,
                "last_name": teacher.profile.last_name,
            },

            "classes": teacher.classes.filter(
                church=church
            ).count(),

            "total_lessons": total_lessons,

            "completed_lessons": completed_lessons,

            "cancelled_lessons": cancelled_lessons,

            "lesson_completion_rate":
                lesson_completion_rate,

            "student_attendance_rate":
                attendance_rate,

            "performance_score":
                performance_score,
        })

    results.sort(
        key=lambda item: item["performance_score"],
        reverse=True
    )

    average_performance = 0

    if results:
        average_performance = round(
            sum(
                item["performance_score"]
                for item in results
            ) / len(results),
            2
        )

    return {
        "total_teachers": len(results),
        "average_performance": average_performance,
        "teachers": results,
    }

