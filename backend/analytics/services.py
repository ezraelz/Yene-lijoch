from datetime import timedelta, datetime, date
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.timesince import timesince

from students.models import Student
from teachers.models import Teacher
from classes.models import ClassRoom
from events.models import Event
from attendance.models import Attendance
from lessons.models import Lesson
from announcements.models import Announcement
from organizations.models import Organization, OrganizationMembership
from django.contrib.auth import get_user_model

from .utils import calculate_growth, first_of_month, previous_month, get_display_name

User = get_user_model()


class AnalyticsService:
    """Service for dashboard analytics calculations."""
    
    @staticmethod
    def get_basic_totals():
        return {
            "total_students": Student.objects.count(),
            "total_teachers": Teacher.objects.count(),
            "total_classes": ClassRoom.objects.count(),
        }
    
    @staticmethod
    def get_student_growth(today):
        first_day_current_month = today.replace(day=1)
        first_day_previous_month = previous_month(first_day_current_month)
        
        return calculate_growth(
            Student.objects.filter(enrollment_date__lt=first_day_current_month).count(),
            Student.objects.filter(enrollment_date__lt=first_day_previous_month).count(),
        )
    
    @staticmethod
    def get_teacher_growth(today):
        first_day_current_month = today.replace(day=1)
        first_day_previous_month = previous_month(first_day_current_month)
        
        return calculate_growth(
            Teacher.objects.filter(employment_date__lt=first_day_current_month).count(),
            Teacher.objects.filter(employment_date__lt=first_day_previous_month).count(),
        )
    
    @staticmethod
    def get_today_attendance(today):
        today_attendance = Attendance.objects.filter(recorded_at__date=today)
        today_total = today_attendance.count()
        today_present = today_attendance.filter(status="present").count()
        
        return {
            "percentage": round((today_present / today_total) * 100, 1) if today_total else 0,
            "total": today_total,
            "present": today_present,
        }
    
    @staticmethod
    def get_yesterday_attendance(today):
        yesterday = today - timedelta(days=1)
        yesterday_attendance = Attendance.objects.filter(recorded_at__date=yesterday)
        yesterday_total = yesterday_attendance.count()
        yesterday_present = yesterday_attendance.filter(status="present").count()
        
        return {
            "percentage": (yesterday_present / yesterday_total) * 100 if yesterday_total else 0,
            "total": yesterday_total,
            "present": yesterday_present,
        }
    
    @staticmethod
    def get_attendance_stats():
        return Attendance.objects.aggregate(
            total=Count("id"),
            present=Count("id", filter=Q(status="present")),
            absent=Count("id", filter=Q(status="absent")),
            late=Count("id", filter=Q(status="late")),
        )
    
    @staticmethod
    def get_performance_metrics():
        total_attendance = Attendance.objects.count()
        
        if total_attendance == 0:
            return [
                {"label": "Attendance", "value": 0, "target": 90},
                {"label": "Present", "value": 0, "target": 90},
                {"label": "Punctuality", "value": 0, "target": 90},
            ]
        
        present = Attendance.objects.filter(status="present").count()
        late = Attendance.objects.filter(status="late").count()
        
        attendance_percentage = round((present / total_attendance) * 100, 1)
        punctuality_percentage = round((present / total_attendance) * 100, 1)
        attendance_rate = round(((present + late) / total_attendance) * 100, 1)
        
        return [
            {"label": "Attendance", "value": attendance_rate, "target": 90},
            {"label": "Present", "value": attendance_percentage, "target": 90},
            {"label": "Punctuality", "value": punctuality_percentage, "target": 85},
        ]


class EventService:
    """Service for event-related operations."""
    
    @staticmethod
    def get_upcoming_events(today, limit=10):
        events = Event.objects.filter(created_at__gte=today).order_by("created_at", "start_datetime")[:limit]
        
        return [
            {
                "id": str(event.id),
                "title": event.title,
                "date": event.created_at.isoformat(),
                "time": event.start_datetime.strftime("%H:%M") if event.start_datetime else "",
                "location": getattr(event, "location", None),
                "type": getattr(event, "type", "school"),
                "description": getattr(event, "description", ""),
            }
            for event in events
        ]


class ActivityService:
    """Service for recent activity feed."""
    
    @staticmethod
    def get_recent_activities(limit=10):
        activities = []
        
        # Recent students
        for student in Student.objects.order_by("-id")[:5]:
            activities.append({
                "id": f"student-{student.id}",
                "type": "student",
                "title": "New student",
                "description": f"{student.profile.get_full_name()} was added.",
                "createdAt": getattr(student, "created_at", timezone.now()).isoformat(),
                "user": None,
            })
        
        # Recent teachers
        for teacher in Teacher.objects.order_by("-id")[:5]:
            activities.append({
                "id": f"teacher-{teacher.id}",
                "type": "teacher",
                "title": "Teacher added",
                "description": f"{get_teacher_name(teacher)} was added.",
                "createdAt": getattr(teacher, "created_at", timezone.now()).isoformat(),
                "user": None,
            })
        
        # Recent events
        for event in Event.objects.order_by("-id")[:5]:
            activities.append({
                "id": f"event-{event.id}",
                "type": "event",
                "title": "New event",
                "description": f"{event.title} was created.",
                "createdAt": getattr(event, "created_at", timezone.now()).isoformat(),
                "user": None,
            })
        
        # Sort newest first
        activities.sort(key=lambda item: item["createdAt"], reverse=True)
        return activities[:limit]


class PlatformService:
    """Service for platform admin operations."""
    
    @staticmethod
    def get_platform_stats(today):
        first_this_month = first_of_month(today)
        first_prev_month = previous_month(today)
        
        total_organizations = Organization.objects.exclude(status=Organization.Status.REJECTED).count()
        approved_organizations = Organization.objects.filter(status=Organization.Status.APPROVED).count()
        pending_organizations = Organization.objects.filter(status=Organization.Status.PENDING).count()
        
        approved_before_this_month = Organization.objects.filter(
            status=Organization.Status.APPROVED,
            approved_at__date__lt=first_this_month,
        ).count()
        approved_before_prev_month = Organization.objects.filter(
            status=Organization.Status.APPROVED,
            approved_at__date__lt=first_prev_month,
        ).count()
        growth = calculate_growth(approved_before_this_month, approved_before_prev_month)
        
        total_users = User.objects.count()
        pending_leadership_requests = OrganizationMembership.objects.filter(
            status=OrganizationMembership.Status.PENDING,
            role__in=OrganizationMembership.LEADERSHIP_ROLES,
        ).count()
        pending_approvals = pending_organizations + pending_leadership_requests
        
        return {
            "totalOrganizations": total_organizations,
            "approvedOrganizations": approved_organizations,
            "pendingOrganizations": pending_organizations,
            "totalUsers": total_users,
            "growth": growth,
            "pendingApprovals": pending_approvals,
            "activeSubscriptions": None,
            "revenue": None,
        }
    
    @staticmethod
    def get_organization_growth(today, months=6):
        cursor = first_of_month(today)
        month_starts = [cursor]
        for _ in range(months - 1):
            cursor = previous_month(cursor)
            month_starts.append(cursor)
        month_starts.reverse()
        
        labels = []
        values = []
        
        for i, start in enumerate(month_starts):
            if i + 1 < len(month_starts):
                end = month_starts[i + 1]
            else:
                end = today + timedelta(days=1)
            
            count = Organization.objects.filter(
                status=Organization.Status.APPROVED,
                approved_at__date__gte=start,
                approved_at__date__lt=end,
            ).count()
            
            labels.append(start.strftime("%b"))
            values.append(count)
        
        current_total = sum(values)
        previous_period_total = Organization.objects.filter(
            status=Organization.Status.APPROVED,
            approved_at__date__lt=month_starts[0],
        ).count()
        growth = calculate_growth(current_total, previous_period_total) if previous_period_total else (
            100.0 if current_total > 0 else 0.0
        )
        
        return {"labels": labels, "values": values, "growth": growth}
    
    @staticmethod
    def _ensure_timezone_aware(dt):
        """Ensure a datetime is timezone-aware."""
        if dt is None:
            return None
        if timezone.is_naive(dt):
            return timezone.make_aware(dt)
        return dt
    
    @staticmethod
    def get_platform_activities(limit=10):
        events = []
        
        # Organizations
        for org in Organization.objects.exclude(status=Organization.Status.REJECTED).order_by("-created_at")[:limit * 2]:
            events.append({
                "id": f"org-created-{org.id}",
                "type": "organization",
                "title": "New organization submitted",
                "description": f"{org.name} was submitted for review.",
                "timestamp": org.created_at,
                "user": get_display_name(org.created_by),
            })
            if org.status == Organization.Status.APPROVED and org.approved_at:
                events.append({
                    "id": f"org-approved-{org.id}",
                    "type": "organization",
                    "title": "Organization approved",
                    "description": f"{org.name} is now active on the platform.",
                    "timestamp": org.approved_at,
                    "user": get_display_name(org.approved_by),
                })
        
        # Leadership memberships
        for membership in OrganizationMembership.objects.filter(
            role__in=OrganizationMembership.LEADERSHIP_ROLES,
            status=OrganizationMembership.Status.APPROVED,
            reviewed_at__isnull=False,
        ).select_related("organization", "user").order_by("-reviewed_at")[:limit * 2]:
            events.append({
                "id": f"membership-{membership.id}",
                "type": "user",
                "title": f"{membership.get_role_display()} approved",
                "description": (
                    f"{get_display_name(membership.user)} is now "
                    f"{membership.get_role_display()} of {membership.organization.name}."
                ),
                "timestamp": membership.reviewed_at,
                "user": get_display_name(membership.reviewed_by),
            })
        
        # New users
        if hasattr(User, "created_at"):
            for user in User.objects.order_by("-created_at")[:limit]:
                user_created_at = getattr(user, "created_at", None)
                if user_created_at is None:
                    user_created_at = timezone.now()
                events.append({
                    "id": f"user-{user.pk}",
                    "type": "user",
                    "title": "New account created",
                    "description": f"{get_display_name(user)} signed up.",
                    "timestamp": user_created_at,
                    "user": "System",
                })
        
        # Filter out None timestamps
        events = [e for e in events if e["timestamp"] is not None]
        
        # Normalize all timestamps to timezone-aware datetime objects
        for event in events:
            ts = event["timestamp"]
            
            # Handle datetime objects
            if isinstance(ts, datetime):
                # Make timezone-aware if naive
                if timezone.is_naive(ts):
                    event["timestamp"] = timezone.make_aware(ts)
                continue
            
            # Handle date objects
            elif isinstance(ts, date):
                # Convert date to datetime at midnight, then make aware
                dt = datetime.combine(ts, datetime.min.time())
                event["timestamp"] = timezone.make_aware(dt)
            
            # Handle string or other types
            else:
                try:
                    dt = datetime.fromisoformat(str(ts))
                    if timezone.is_naive(dt):
                        event["timestamp"] = timezone.make_aware(dt)
                    else:
                        event["timestamp"] = dt
                except (ValueError, TypeError, AttributeError):
                    # Fallback to current time
                    event["timestamp"] = timezone.now()
        
        # Sort by timestamp (now all are timezone-aware datetimes)
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


class SystemHealthService:
    """Service for system health monitoring."""
    
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


# Helper function that was referenced but missing
def get_teacher_name(teacher):
    if hasattr(teacher, "get_full_name"):
        return teacher.get_full_name()
    if hasattr(teacher, "profile"):
        return teacher.profile.get_full_name()
    return str(teacher)
