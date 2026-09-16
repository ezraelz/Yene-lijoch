from datetime import timedelta, datetime, date

from django.db.models import Count, Q
from django.utils import timezone
from django.utils.timesince import timesince
from django.contrib.auth import get_user_model

from students.models import Student
from teachers.models import Teacher
from classes.models import ClassRoom
from events.models import Event
from attendance.models import Attendance
from lessons.models import Lesson
from medias.models import MediaItem
from announcements.models import Announcement
from organizations.models import Organization, OrganizationMembership

from .utils import calculate_growth, first_of_month, previous_month, get_display_name
from organizations.utils import (
    is_superuser,
    is_admin,
    get_user_organization,
)
User = get_user_model()


# ======================================================================
# Scope helpers
# ======================================================================

def scope_queryset(qs, user, org_field="organization"):
    """
    Apply organization scoping to any queryset that has an
    `organization`-like field. Superusers pass through unchanged.
    """
    if is_superuser(user):
        return qs
    org = get_user_organization(user)
    if not org:
        return qs.none()
    return qs.filter(**{org_field: org})


def resolve_scope(user, organization=None):
    """
    Return the organization a caller should be scoped to.

    - Superusers: whatever `organization` they passed (or None for global).
    - Admins:     their own organization.
    """
    if is_superuser(user):
        return organization
    return get_user_organization(user)


def get_teacher_name(teacher):
    if hasattr(teacher, "get_full_name"):
        return teacher.get_full_name()
    if hasattr(teacher, "profile"):
        return teacher.profile.get_full_name()
    return str(teacher)


# ======================================================================
# Dashboard analytics
# ======================================================================

class AnalyticsService:
    """
    Dashboard totals + growth for the admin home screen.

    Every method accepts a `user` (and optionally `organization`) so it
    scopes automatically.
    """

    # ------------------------------------------------------------------
    @staticmethod
    def get_basic_totals(user=None, organization=None):
        """
        Returns the four counters the AdminHome renders:
            media, curriculum, students, events
        """
        org = resolve_scope(user, organization) if user else organization

        students_qs = Student.objects.all()
        classes_qs = ClassRoom.objects.all()
        lessons_qs = Lesson.objects.all()
        events_qs = Event.objects.all()
        media_qs = MediaItem.objects.all()

        if org:
            students_qs = students_qs.filter(organization=org)
            classes_qs = classes_qs.filter(organization=org)
            lessons_qs = lessons_qs.filter(classroom__organization=org)
            events_qs = events_qs.filter(organization=org)
            media_qs = media_qs.filter(organization=org)

        return {
            "total_students": students_qs.count(),
            "total_teachers": Teacher.objects.count(),  # optionally scoped below
            "total_classes": classes_qs.count(),
            "total_lessons": lessons_qs.count(),
            "total_events": events_qs.count(),
            "total_media": media_qs.count(),
        }

    # ------------------------------------------------------------------
    @staticmethod
    def get_student_growth(today, user=None, organization=None):
        org = resolve_scope(user, organization) if user else organization
        qs = Student.objects.all()
        if org:
            qs = qs.filter(organization=org)

        first_this = first_of_month(today)
        first_prev = previous_month(first_this)

        return calculate_growth(
            qs.filter(enrollment_date__lt=first_this).count(),
            qs.filter(enrollment_date__lt=first_prev).count(),
        )

    # ------------------------------------------------------------------
    @staticmethod
    def get_teacher_growth(today, user=None, organization=None):
        org = resolve_scope(user, organization) if user else organization
        qs = Teacher.objects.all()
        if org:
            # Adjust the lookup path to your Teacher schema
            qs = qs.filter(profile__organization__organization=org)

        first_this = first_of_month(today)
        first_prev = previous_month(first_this)

        return calculate_growth(
            qs.filter(employment_date__lt=first_this).count(),
            qs.filter(employment_date__lt=first_prev).count(),
        )

    # ------------------------------------------------------------------
    @staticmethod
    def get_today_attendance(today, user=None, organization=None):
        org = resolve_scope(user, organization) if user else organization
        qs = Attendance.objects.filter(recorded_at__date=today)
        if org:
            qs = qs.filter(student__organization=org)

        total = qs.count()
        present = qs.filter(status="present").count()

        return {
            "percentage": round((present / total) * 100, 1) if total else 0,
            "total": total,
            "present": present,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def get_yesterday_attendance(today, user=None, organization=None):
        yesterday = today - timedelta(days=1)
        org = resolve_scope(user, organization) if user else organization
        qs = Attendance.objects.filter(recorded_at__date=yesterday)
        if org:
            qs = qs.filter(student__organization=org)

        total = qs.count()
        present = qs.filter(status="present").count()

        return {
            "percentage": (present / total) * 100 if total else 0,
            "total": total,
            "present": present,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def get_attendance_stats(user=None, organization=None):
        org = resolve_scope(user, organization) if user else organization
        qs = Attendance.objects.all()
        if org:
            qs = qs.filter(student__organization=org)

        return qs.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="present")),
            absent=Count("id", filter=Q(status="absent")),
            late=Count("id", filter=Q(status="late")),
        )

    # ------------------------------------------------------------------
    @staticmethod
    def get_performance_metrics(user=None, organization=None):
        org = resolve_scope(user, organization) if user else organization
        qs = Attendance.objects.all()
        if org:
            qs = qs.filter(student__organization=org)

        total = qs.count()
        if total == 0:
            return [
                {"label": "Attendance", "value": 0, "target": 90},
                {"label": "Present", "value": 0, "target": 90},
                {"label": "Punctuality", "value": 0, "target": 85},
            ]

        present = qs.filter(status="present").count()
        late = qs.filter(status="late").count()

        attendance_rate = round(((present + late) / total) * 100, 1)
        present_rate = round((present / total) * 100, 1)
        punctuality_rate = round((present / total) * 100, 1)

        return [
            {"label": "Attendance", "value": attendance_rate, "target": 90},
            {"label": "Present", "value": present_rate, "target": 90},
            {"label": "Punctuality", "value": punctuality_rate, "target": 85},
        ]


# ======================================================================
# Event service
# ======================================================================

class EventService:
    """Upcoming events scoped to the caller's organization."""

    @staticmethod
    def get_upcoming_events(today, limit=10, user=None, organization=None):
        org = resolve_scope(user, organization) if user else organization

        # Upcoming = start_datetime >= now (or today at midnight).
        qs = Event.objects.filter(
            start_datetime__gte=timezone.now(),
            published=True,
        ).order_by("start_datetime")

        if org:
            qs = qs.filter(organization=org)

        events = qs[:limit]

        return [
            {
                "id": str(event.id),
                "title": event.title,
                "date": event.display_date,
                "time": event.display_time,
                "location": event.location or "",
                "type": event.event_type,
                "audience": event.audience,
                "description": event.description or "",
                "start_datetime": event.start_datetime.isoformat(),
            }
            for event in events
        ]


# ======================================================================
# Activity feed
# ======================================================================

class ActivityService:
    """
    Recent activity feed used by the admin home.

    Every query is scoped to the caller's organization (or global for
    superusers).
    """

    @staticmethod
    def get_recent_activities(limit=10, user=None, organization=None):
        org = resolve_scope(user, organization) if user else organization
        activities = []

        # ----- Students ----------------------------------------------
        students_qs = Student.objects.select_related("profile").order_by("-id")
        if org:
            students_qs = students_qs.filter(organization=org)

        for student in students_qs[:5]:
            activities.append({
                "id": f"student-{student.id}",
                "type": "student",
                "title": "New student",
                "description": f"{student.full_name} was added.",
                "createdAt": (
                    student.created_at.isoformat()
                    if hasattr(student, "created_at") and student.created_at
                    else timezone.now().isoformat()
                ),
                "user": None,
            })

        # ----- Teachers ----------------------------------------------
        teachers_qs = Teacher.objects.select_related("profile").order_by("-id")
        if org:
            teachers_qs = teachers_qs.filter(profile__organization__organization=org)

        for teacher in teachers_qs[:5]:
            activities.append({
                "id": f"teacher-{teacher.id}",
                "type": "teacher",
                "title": "Teacher added",
                "description": f"{get_teacher_name(teacher)} was added.",
                "createdAt": timezone.now().isoformat(),
                "user": None,
            })

        # ----- Events ------------------------------------------------
        events_qs = Event.objects.order_by("-id")
        if org:
            events_qs = events_qs.filter(organization=org)

        for event in events_qs[:5]:
            activities.append({
                "id": f"event-{event.id}",
                "type": "event",
                "title": "New event",
                "description": f"{event.title} was created.",
                "createdAt": (
                    event.created_at.isoformat()
                    if event.created_at
                    else timezone.now().isoformat()
                ),
                "user": None,
            })

        # ----- Media -------------------------------------------------
        media_qs = MediaItem.objects.order_by("-created_at")
        if org:
            media_qs = media_qs.filter(organization=org)

        for item in media_qs[:5]:
            activities.append({
                "id": f"media-{item.id}",
                "type": "media",
                "title": "New media uploaded",
                "description": f"{item.title} ({item.get_kind_display()}) was uploaded.",
                "createdAt": item.created_at.isoformat(),
                "user": None,
            })

        # ----- Lessons -----------------------------------------------
        lessons_qs = Lesson.objects.order_by("-created_at")
        if org:
            lessons_qs = lessons_qs.filter(classroom__organization=org)

        for lesson in lessons_qs[:5]:
            activities.append({
                "id": f"lesson-{lesson.id}",
                "type": "lesson",
                "title": "New lesson",
                "description": f"{lesson.title} was added to the curriculum.",
                "createdAt": (
                    lesson.created_at.isoformat()
                    if lesson.created_at
                    else timezone.now().isoformat()
                ),
                "user": None,
            })

        # Sort newest first and trim.
        activities.sort(key=lambda item: item["createdAt"], reverse=True)
        return activities[:limit]


# ======================================================================
# Platform service (superuser only)
# ======================================================================

class PlatformService:
    """
    Platform-wide stats. Intended for superusers; org admins should not
    call these endpoints (or the view layer should block them).
    """

    @staticmethod
    def get_platform_stats(today, user=None):
        # Org admins only see their own org's stats.
        if user and not is_superuser(user):
            return PlatformService._get_org_stats(today, user)

        first_this_month = first_of_month(today)
        first_prev_month = previous_month(today)

        total_orgs = (
            Organization.objects
            .exclude(status=Organization.Status.REJECTED)
            .count()
        )
        approved_orgs = Organization.objects.filter(
            status=Organization.Status.APPROVED
        ).count()
        pending_orgs = Organization.objects.filter(
            status=Organization.Status.PENDING
        ).count()

        approved_before_this = Organization.objects.filter(
            status=Organization.Status.APPROVED,
            approved_at__date__lt=first_this_month,
        ).count()
        approved_before_prev = Organization.objects.filter(
            status=Organization.Status.APPROVED,
            approved_at__date__lt=first_prev_month,
        ).count()

        growth = calculate_growth(approved_before_this, approved_before_prev)

        pending_leadership = OrganizationMembership.objects.filter(
            status=OrganizationMembership.Status.PENDING,
            role__in=OrganizationMembership.LEADERSHIP_ROLES,
        ).count()

        return {
            "totalOrganizations": total_orgs,
            "approvedOrganizations": approved_orgs,
            "pendingOrganizations": pending_orgs,
            "totalUsers": User.objects.count(),
            "growth": growth,
            "pendingApprovals": pending_orgs + pending_leadership,
            "activeSubscriptions": None,
            "revenue": None,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def _get_org_stats(today, user):
        """Single-org stats for an org admin."""
        org = get_user_organization(user)
        if not org:
            return {
                "totalOrganizations": 0,
                "approvedOrganizations": 0,
                "pendingOrganizations": 0,
                "totalUsers": 0,
                "growth": 0.0,
                "pendingApprovals": 0,
                "activeSubscriptions": None,
                "revenue": None,
            }

        memberships = OrganizationMembership.objects.filter(
            organization=org
        )

        first_this = first_of_month(today)
        first_prev = previous_month(first_this)

        members_before_this = memberships.filter(
            created_at__date__lt=first_this
        ).count()
        members_before_prev = memberships.filter(
            created_at__date__lt=first_prev
        ).count()

        return {
            "totalOrganizations": 1,
            "approvedOrganizations": 1 if org.status == Organization.Status.APPROVED else 0,
            "pendingOrganizations": 1 if org.status == Organization.Status.PENDING else 0,
            "totalUsers": memberships.count(),
            "growth": calculate_growth(members_before_this, members_before_prev),
            "pendingApprovals": memberships.filter(
                status=OrganizationMembership.Status.PENDING,
                role__in=OrganizationMembership.LEADERSHIP_ROLES,
            ).count(),
            "activeSubscriptions": None,
            "revenue": None,
        }

    # ------------------------------------------------------------------
    @staticmethod
    def get_organization_growth(today, months=6, user=None, organization=None):
        """
        Month-by-month approved-org counts.

        For org admins this returns a single-org growth line of their own
        membership count instead of the platform-wide org chart.
        """
        if user and not is_superuser(user):
            return PlatformService._get_membership_growth(today, user, months)

        cursor = first_of_month(today)
        month_starts = [cursor]
        for _ in range(months - 1):
            cursor = previous_month(cursor)
            month_starts.append(cursor)
        month_starts.reverse()

        labels, values = [], []
        for i, start in enumerate(month_starts):
            end = month_starts[i + 1] if i + 1 < len(month_starts) else today + timedelta(days=1)
            count = Organization.objects.filter(
                status=Organization.Status.APPROVED,
                approved_at__date__gte=start,
                approved_at__date__lt=end,
            ).count()
            labels.append(start.strftime("%b"))
            values.append(count)

        current_total = sum(values)
        previous_total = Organization.objects.filter(
            status=Organization.Status.APPROVED,
            approved_at__date__lt=month_starts[0],
        ).count()

        growth = calculate_growth(current_total, previous_total) if previous_total else (
            100.0 if current_total > 0 else 0.0
        )

        return {"labels": labels, "values": values, "growth": growth}

    # ------------------------------------------------------------------
    @staticmethod
    def _get_membership_growth(today, user, months=6):
        org = get_user_organization(user)
        cursor = first_of_month(today)
        month_starts = [cursor]
        for _ in range(months - 1):
            cursor = previous_month(cursor)
            month_starts.append(cursor)
        month_starts.reverse()

        labels, values = [], []
        for i, start in enumerate(month_starts):
            end = month_starts[i + 1] if i + 1 < len(month_starts) else today + timedelta(days=1)
            count = OrganizationMembership.objects.filter(
                organization=org,
                created_at__date__gte=start,
                created_at__date__lt=end,
            ).count()
            labels.append(start.strftime("%b"))
            values.append(count)

        current_total = sum(values)
        previous_total = OrganizationMembership.objects.filter(
            organization=org,
            created_at__date__lt=month_starts[0],
        ).count()
        growth = calculate_growth(current_total, previous_total) if previous_total else (
            100.0 if current_total > 0 else 0.0
        )

        return {"labels": labels, "values": values, "growth": growth}

    # ------------------------------------------------------------------
    @staticmethod
    def get_platform_activities(limit=10, user=None, organization=None):
        """
        Activity feed for the platform dashboard.

        Org admins only see activity scoped to their organization.
        """
        if user and not is_superuser(user):
            return PlatformService._get_org_activities(user, limit)

        events = []

        # ----- Organizations ----------------------------------------
        orgs_qs = (
            Organization.objects
            .exclude(status=Organization.Status.REJECTED)
            .order_by("-created_at")[: limit * 2]
        )
        for org in orgs_qs:
            events.append({
                "id": f"org-created-{org.id}",
                "type": "organization",
                "title": "New organization submitted",
                "description": f"{org.name} was submitted for review.",
                "timestamp": org.created_at,
                "user": get_display_name(getattr(org, "created_by", None)),
            })
            if org.status == Organization.Status.APPROVED and org.approved_at:
                events.append({
                    "id": f"org-approved-{org.id}",
                    "type": "organization",
                    "title": "Organization approved",
                    "description": f"{org.name} is now active on the platform.",
                    "timestamp": org.approved_at,
                    "user": get_display_name(getattr(org, "approved_by", None)),
                })

        # ----- Leadership memberships --------------------------------
        memberships_qs = (
            OrganizationMembership.objects
            .filter(
                role__in=OrganizationMembership.LEADERSHIP_ROLES,
                status=OrganizationMembership.Status.APPROVED,
                reviewed_at__isnull=False,
            )
            .select_related("organization", "user")
            .order_by("-reviewed_at")[: limit * 2]
        )
        for membership in memberships_qs:
            events.append({
                "id": f"membership-{membership.id}",
                "type": "user",
                "title": f"{membership.get_role_display()} approved",
                "description": (
                    f"{get_display_name(membership.user)} is now "
                    f"{membership.get_role_display()} of "
                    f"{membership.organization.name}."
                ),
                "timestamp": membership.reviewed_at,
                "user": get_display_name(getattr(membership, "reviewed_by", None)),
            })

        # ----- New users ---------------------------------------------
        if hasattr(User, "created_at"):
            for user_obj in User.objects.order_by("-created_at")[:limit]:
                ts = getattr(user_obj, "created_at", None) or timezone.now()
                events.append({
                    "id": f"user-{user_obj.pk}",
                    "type": "user",
                    "title": "New account created",
                    "description": f"{get_display_name(user_obj)} signed up.",
                    "timestamp": ts,
                    "user": "System",
                })

        return PlatformService._serialize_activities(events, limit)

    # ------------------------------------------------------------------
    @staticmethod
    def _get_org_activities(user, limit=10):
        """Activity feed scoped to an org admin's organization."""
        org = get_user_organization(user)
        if not org:
            return []

        events = []

        # Students in this org
        for student in Student.objects.filter(organization=org).order_by("-id")[: limit]:
            events.append({
                "id": f"student-{student.id}",
                "type": "student",
                "title": "New student enrolled",
                "description": f"{student.full_name} was added.",
                "timestamp": getattr(student, "created_at", None) or timezone.now(),
                "user": None,
            })

        # Media in this org
        for item in MediaItem.objects.filter(organization=org).order_by("-created_at")[: limit]:
            events.append({
                "id": f"media-{item.id}",
                "type": "media",
                "title": "New media uploaded",
                "description": f"{item.title} ({item.get_kind_display()}) was uploaded.",
                "timestamp": item.created_at,
                "user": None,
            })

        # Events in this org
        for event in Event.objects.filter(organization=org).order_by("-created_at")[: limit]:
            events.append({
                "id": f"event-{event.id}",
                "type": "event",
                "title": "New event created",
                "description": f"{event.title} was scheduled.",
                "timestamp": event.created_at,
                "user": None,
            })

        # Lessons in this org
        for lesson in Lesson.objects.filter(
            classroom__organization=org
        ).order_by("-created_at")[: limit]:
            events.append({
                "id": f"lesson-{lesson.id}",
                "type": "lesson",
                "title": "New lesson published",
                "description": f"{lesson.title} was added to the curriculum.",
                "timestamp": getattr(lesson, "created_at", None) or timezone.now(),
                "user": None,
            })

        return PlatformService._serialize_activities(events, limit)

    # ------------------------------------------------------------------
    @staticmethod
    def _serialize_activities(events, limit):
        """Normalise timestamps, sort, trim, and JSON-serialize."""
        events = [e for e in events if e["timestamp"] is not None]

        for event in events:
            ts = event["timestamp"]
            if isinstance(ts, datetime):
                if timezone.is_naive(ts):
                    event["timestamp"] = timezone.make_aware(ts)
            elif isinstance(ts, date):
                dt = datetime.combine(ts, datetime.min.time())
                event["timestamp"] = timezone.make_aware(dt)
            else:
                try:
                    dt = datetime.fromisoformat(str(ts))
                    event["timestamp"] = (
                        timezone.make_aware(dt) if timezone.is_naive(dt) else dt
                    )
                except (ValueError, TypeError, AttributeError):
                    event["timestamp"] = timezone.now()

        events.sort(key=lambda e: e["timestamp"], reverse=True)
        events = events[:limit]

        return [
            {
                "id": e["id"],
                "type": e["type"],
                "title": e["title"],
                "description": e["description"],
                "time": f"{timesince(e['timestamp'])} ago",
                "createdAt": e["timestamp"].isoformat(),
                "user": e["user"],
            }
            for e in events
        ]


# ======================================================================
# System health (superuser only)
# ======================================================================

class SystemHealthService:
    """
    System health is inherently platform-wide; it should only be exposed
    to superusers. The view layer should enforce that.
    """

    @staticmethod
    def get_system_health():
        import time
        from .utils import format_uptime

        start = time.perf_counter()
        _PROCESS_START = time.time()

        try:
            import psutil
            server_load = psutil.cpu_percent(interval=0.1)
            memory_percent = psutil.virtual_memory().percent
        except ImportError:
            server_load = None
            memory_percent = None

        uptime_seconds = time.time() - _PROCESS_START
        uptime_display = format_uptime(uptime_seconds)
        response_time_ms = round((time.perf_counter() - start) * 1000, 1)

        if server_load is None:
            status_value = "warning"
            label_note = "psutil not installed — install it for real CPU/memory metrics."
        elif server_load > 90 or (memory_percent or 0) > 90:
            status_value = "critical"
            label_note = None
        elif server_load > 70 or (memory_percent or 0) > 75:
            status_value = "warning"
            label_note = None
        else:
            status_value = "healthy"
            label_note = None

        payload = {
            "status": status_value,
            "uptime": uptime_display,
            "responseTime": response_time_ms,
            "serverLoad": server_load,
            "memoryPercent": memory_percent,
            "activeJobs": None,
        }
        if label_note:
            payload["note"] = label_note

        return payload
    