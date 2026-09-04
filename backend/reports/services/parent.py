from parents.models import Parent
from .common import get_organization_for_user


def get_parent_report(user):
    """
    Generate a parent summary report.
    """

    organization = get_organization_for_user(user)

    if not organization:
        return None

    parents = Parent.objects.filter(
        organization=organization
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

