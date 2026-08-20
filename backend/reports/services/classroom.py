from classes.models import ClassRoom
from .common import get_church_for_user

def get_classroom_report(user):

    church = get_church_for_user(user)

    if not church:
        return None

    classrooms = ClassRoom.objects.filter(
        church=church
    ).select_related(
        "teacher__profile"
    ).prefetch_related(
        "students"
    )

    results = []

    for classroom in classrooms:

        results.append({
            "id": classroom.id,
            "name": classroom.name,
            "age_group": classroom.age_group,
            "room": classroom.room,
            "status": classroom.status,
            "teacher": (
                {
                    "id": classroom.teacher.id,
                    "first_name":
                        classroom.teacher.profile.first_name,
                    "last_name":
                        classroom.teacher.profile.last_name,
                }
                if classroom.teacher
                else None
            ),
            "student_count":
                classroom.students.count(),
            "start_date":
                classroom.start_date,
            "end_date":
                classroom.end_date,
        })

    return {
        "total": classrooms.count(),

        "active": classrooms.filter(
            status="active"
        ).count(),

        "inactive": classrooms.filter(
            status="inactive"
        ).count(),

        "completed": classrooms.filter(
            status="completed"
        ).count(),

        "classes": results,
    }

