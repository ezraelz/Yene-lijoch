from .attendance import get_attendance_summary
from .curriculum import get_curriculum_report
from .enrollment import get_enrollment_report
from .teacher import get_teacher_performance_report
from .classroom import get_classroom_report

def get_health_report(user):

    attendance = get_attendance_summary(user)
    curriculum = get_curriculum_report(user)
    enrollment = get_enrollment_report(user)
    teachers = get_teacher_performance_report(user)
    classrooms = get_classroom_report(user)

    if not all([
        attendance,
        curriculum,
        enrollment,
        teachers,
        classrooms,
    ]):
        return None

    attendance_score = (
        attendance["attendance_percentage"]
    )

    curriculum_score = (
        curriculum["completion_percentage"]
    )

    teacher_score = (
        teachers["average_performance"]
    )

    enrollment_score = 100 if (
        enrollment["active_students"] > 0
    ) else 0

    class_score = 0

    if classrooms["total"] > 0:
        class_score = round(
            (
                classrooms["active"] /
                classrooms["total"]
            ) * 100,
            2
        )

    health_score = round(
        (
            attendance_score * 0.30
            +
            curriculum_score * 0.25
            +
            teacher_score * 0.20
            +
            class_score * 0.15
            +
            enrollment_score * 0.10
        ),
        2
    )

    if health_score >= 90:
        rating = "Excellent"
        message = "All classes running on track"

    elif health_score >= 75:
        rating = "Good"
        message = "Most classes are running well"

    elif health_score >= 60:
        rating = "Needs Attention"
        message = "Some areas require attention"

    else:
        rating = "Critical"
        message = "Several areas require immediate attention"

    return {
        "score": health_score,
        "rating": rating,
        "message": message,

        "components": {
            "attendance": attendance_score,
            "curriculum": curriculum_score,
            "teacher_performance": teacher_score,
            "class_health": class_score,
            "enrollment": enrollment_score,
        },
    }

