from datetime import timedelta
from django.utils import timezone

def calculate_growth(current: int, previous: int) -> float:
    """
    Calculate percentage growth.
    
    Example:
    previous = 100
    current = 110
    result = 10.0
    """
    if previous == 0:
        return 100.0 if current > 0 else 0.0
    return round(((current - previous) / previous) * 100, 1)


def first_of_month(d):
    return d.replace(day=1)


def previous_month(d):
    first = first_of_month(d)
    if first.month == 1:
        return first.replace(year=first.year - 1, month=12)
    return first.replace(month=first.month - 1)


def get_display_name(user):
    if not user:
        return "Unknown"
    full_name = f"{getattr(user, 'first_name', '')} {getattr(user, 'last_name', '')}".strip()
    return full_name or getattr(user, "username", str(user))


def get_created_at(obj):
    created_at = getattr(obj, "created_at", None)
    if created_at:
        return created_at.isoformat()
    return timezone.now().isoformat()


def get_teacher_name(teacher):
    if hasattr(teacher, "get_full_name"):
        return teacher.get_full_name()
    if hasattr(teacher, "profile"):
        return teacher.profile.get_full_name()
    return str(teacher)


def format_uptime(seconds: float) -> str:
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)
    if days:
        return f"{days}d {hours}h"
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"