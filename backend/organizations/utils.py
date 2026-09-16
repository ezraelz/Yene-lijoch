import re

def normalize_org_name(name: str) -> str:
    """
    Normalize an organization name: strip HTML, collapse whitespace,
    lowercase for comparison. Used by models.Organization.save().
    """
    import re
    if not name:
        return ""
    text = re.sub(r"<[^>]*>", "", name)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def sanitize_org_name(name: str) -> str:
    """
    Clean an organization name for display.

    Strips HTML/script tags, trims, and collapses whitespace. Keeps
    original casing and punctuation so the stored `name` reads naturally.
    """
    if not name:
        return ""
    text = str(name)
    # Strip any HTML tags defensively (org names are plain text).
    text = re.sub(r"<[^>]*>", "", text)
    # Collapse whitespace.
    text = re.sub(r"\s+", " ", text).strip()
    return text


def is_superuser(user):
    return bool(
        user and user.is_authenticated and getattr(user, "is_superuser", False)
    )


def is_admin(user):
    if not user or not user.is_authenticated:
        return False
    if getattr(user, "is_superuser", False):
        return True
    role = getattr(user, "role", None)
    return bool(role and getattr(role, "role_name", "") == "admin")


def get_user_organization(user):
    """
    Return the `Organization` the user belongs to, or None for superusers.

    Works for both:
      • request.user is a Profile (normal API case) → user.organization
      • request.user is an auth.User (admin/shell)  → user.profile.organization

    The final `getattr(x, "organization", x)` idiom unwraps an
    OrganizationMembership to its Organization, and is a no-op if `x`
    is already an Organization.
    """
    if not user or not user.is_authenticated:
        return None
    if getattr(user, "is_superuser", False):
        return None

    membership = getattr(user, "organization", None)

    if membership is None:
        profile = getattr(user, "profile", None)
        if profile:
            membership = getattr(profile, "organization", None)

    if not membership:
        return None

    # If membership is already an Organization, `getattr` returns it as-is.
    # If it's an OrganizationMembership, it returns its `.organization` FK.
    return getattr(membership, "organization", membership)


def get_user_membership(user):
    """Return the raw OrganizationMembership or None."""
    if not user or not user.is_authenticated:
        return None
    membership = getattr(user, "organization", None)
    if membership is None:
        profile = getattr(user, "profile", None)
        membership = getattr(profile, "organization", None) if profile else None
    return membership


def get_user_teacher(user):
    """Return the Teacher row for the logged-in user, or None."""
    if not user or not user.is_authenticated:
        return None
    teacher = getattr(user, "teacher_profile", None)
    if teacher is not None:
        return teacher
    profile = getattr(user, "profile", None)
    return getattr(profile, "teacher_profile", None) if profile else None
