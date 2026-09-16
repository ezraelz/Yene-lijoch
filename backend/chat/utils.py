# Profile has no `color` field, and adding one would mean a migration on
# an app you already have in production, so we derive a stable color from
# the row's primary key instead — same parent always gets the same color.

PALETTE = [
    "#5B8DEF", "#F2994A", "#27AE60", "#EB5757",
    "#9B51E0", "#2D9CDB", "#F2C94C", "#56CCF2",
]


def color_for(pk: int) -> str:
    return PALETTE[pk % len(PALETTE)]


def initials_for(profile) -> str:
    first = (profile.first_name or "")[:1]
    last = (profile.last_name or "")[:1]
    letters = (first + last).upper()
    if letters:
        return letters
    fallback = profile.username or (profile.email.split("@")[0] if profile.email else "")
    return (fallback[:2] or "??").upper()


def role_for_user(user):
    """Which side of the conversation this Profile sits on, if any."""
    if hasattr(user, "teacher_profile"):
        return "teacher"
    if hasattr(user, "parent_profile"):
        return "parent"
    return None
