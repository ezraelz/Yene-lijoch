from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.utils import timezone

from .services import (
    AnalyticsService,
    EventService,
    ActivityService,
    PlatformService,
    SystemHealthService,
    get_user_organization,
    is_superuser,
    is_admin,
)
from .serializers import (
    EventSerializer,
    ActivitySerializer,
    AnnouncementSerializer,
    PerformanceIndicatorSerializer,
    PlatformStatSerializer,
    OrganizationGrowthSerializer,
    SystemHealthSerializer,
)
from organizations.permissions import IsSuperUser
from announcements.models import Announcement


# ======================================================================
# Dashboard: authenticated, org-scoped
# ======================================================================

class AnalyticsView(APIView):
    """
    GET /analytics/
    Dashboard counters for the current user's organization.

    - Superuser  → global totals.
    - Org admin  → totals scoped to their organization.
    - Parent / teacher → totals scoped to their organization.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        user = request.user
        org = get_user_organization(user)

        attendance_today = AnalyticsService.get_today_attendance(today, user, org)
        yesterday_attendance = AnalyticsService.get_yesterday_attendance(today, user, org)

        data = {
            **AnalyticsService.get_basic_totals(user, org),
            "attendance_today": attendance_today["percentage"],
            "student_growth": AnalyticsService.get_student_growth(today, user, org),
            "teacher_growth": AnalyticsService.get_teacher_growth(today, user, org),
            "attendance_growth": round(
                attendance_today["percentage"] - yesterday_attendance["percentage"],
                1,
            ),
            "attendance_stats": AnalyticsService.get_attendance_stats(user, org),
        }

        return Response(data, status=status.HTTP_200_OK)


class DashboardEventsView(APIView):
    """
    GET /dashboard/events
    Upcoming events scoped to the current user's organization.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = timezone.localdate()
        user = request.user
        org = get_user_organization(user)

        events = EventService.get_upcoming_events(
            today,
            user=user,
            organization=org,
        )
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardActivitiesView(APIView):
    """
    GET /dashboard/activities
    Recent activity feed scoped to the current user's organization.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        org = get_user_organization(user)

        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        limit = max(1, min(limit, 50))

        activities = ActivityService.get_recent_activities(
            limit=limit,
            user=user,
            organization=org,
        )
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardPerformanceView(APIView):
    """
    GET /dashboard/performance
    Attendance/punctuality indicators scoped to the user's organization.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        org = get_user_organization(user)

        metrics = AnalyticsService.get_performance_metrics(user, org)
        serializer = PerformanceIndicatorSerializer(metrics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardAnnouncementsView(APIView):
    """
    GET /dashboard/announcements
    Latest 10 announcements scoped to the user's organization.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        org = get_user_organization(user)

        qs = Announcement.objects.order_by("-created_at")

        # Scope to the user's org (superusers see all).
        if org and hasattr(Announcement, "organization"):
            qs = qs.filter(organization=org)
        elif org and hasattr(Announcement, "organization_membership__organization"):
            # Adjust if Announcement is scoped via a membership FK.
            qs = qs.filter(organization_membership__organization=org)

        announcements = qs[:10]

        data = [
            {
                "id": str(a.id),
                "title": a.title,
                "description": a.description,
                "createdAt": a.created_at.isoformat(),
                "type": a.type,
            }
            for a in announcements
        ]

        serializer = AnnouncementSerializer(data, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# ======================================================================
# Platform: superuser-only
# ======================================================================

class PlatformStatsView(APIView):
    """
    GET /api/platform/stats/
    Top-level counters for the platform-admin dashboard header cards.

    Superuser only for platform-wide stats. Org admins hitting this
    endpoint get a single-org snapshot (see `PlatformService._get_org_stats`).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not (is_superuser(user) or is_admin(user)):
            raise PermissionDenied("You do not have permission to view platform stats.")

        today = timezone.localdate()
        stats = PlatformService.get_platform_stats(today, user=user)
        serializer = PlatformStatSerializer(stats)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OrganizationGrowthView(APIView):
    """
    GET /api/platform/organization-growth/?months=6
    Monthly approved-organization counts.

    Superusers get the platform-wide series; org admins get a
    single-org membership growth line instead.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not (is_superuser(user) or is_admin(user)):
            raise PermissionDenied("You do not have permission to view growth data.")

        try:
            months = int(request.query_params.get("months", 6))
        except (TypeError, ValueError):
            months = 6
        months = max(1, min(months, 24))

        today = timezone.localdate()
        growth_data = PlatformService.get_organization_growth(
            today,
            months=months,
            user=user,
        )
        serializer = OrganizationGrowthSerializer(growth_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PlatformActivitiesView(APIView):
    """
    GET /api/platform/activities/?limit=10
    Unified recent-activity feed.

    Superusers see platform-wide activity; org admins see their own
    organization's feed.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not (is_superuser(user) or is_admin(user)):
            raise PermissionDenied("You do not have permission to view activities.")

        try:
            limit = int(request.query_params.get("limit", 10))
        except (TypeError, ValueError):
            limit = 10
        limit = max(1, min(limit, 50))

        activities = PlatformService.get_platform_activities(limit, user=user)
        return Response(activities, status=status.HTTP_200_OK)


class SystemHealthView(APIView):
    """
    GET /api/platform/system-health/
    Best-effort, single-process health snapshot.

    Superuser only — system health is inherently platform-wide.
    """

    permission_classes = [IsSuperUser]

    def get(self, request):
        health_data = SystemHealthService.get_system_health()
        serializer = SystemHealthSerializer(health_data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    