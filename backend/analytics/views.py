from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from .services import (
    AnalyticsService,
    EventService,
    ActivityService,
    PlatformService,
    SystemHealthService,
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


class AnalyticsView(APIView):
    """
    Dashboard statistics.
    
    GET /analytics/
    """
    permission_classes = []

    def get(self, request):
        today = timezone.localdate()
        
        analytics = AnalyticsService()
        
        attendance_today = analytics.get_today_attendance(today)
        yesterday_attendance = analytics.get_yesterday_attendance(today)
        
        data = {
            **analytics.get_basic_totals(),
            "attendance_today": attendance_today["percentage"],
            "student_growth": analytics.get_student_growth(today),
            "teacher_growth": analytics.get_teacher_growth(today),
            "attendance_growth": round(attendance_today["percentage"] - yesterday_attendance["percentage"], 1),
            "attendance_stats": analytics.get_attendance_stats(),
        }
        
        return Response(data, status=status.HTTP_200_OK)


class DashboardEventsView(APIView):
    """
    Events displayed on the dashboard.
    
    GET /dashboard/events
    """
    permission_classes = []

    def get(self, request):
        today = timezone.localdate()
        events = EventService.get_upcoming_events(today)
        serializer = EventSerializer(events, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardActivitiesView(APIView):
    """
    Recent dashboard activities.
    
    GET /dashboard/activities
    """
    permission_classes = []

    def get(self, request):
        activities = ActivityService.get_recent_activities()
        serializer = ActivitySerializer(activities, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardPerformanceView(APIView):
    """
    Dashboard performance indicators.
    
    GET /dashboard/performance
    """
    permission_classes = []

    def get(self, request):
        metrics = AnalyticsService.get_performance_metrics()
        serializer = PerformanceIndicatorSerializer(metrics, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DashboardAnnouncementsView(APIView):
    """GET /dashboard/announcements"""
    permission_classes = []

    def get(self, request):
        announcements = Announcement.objects.order_by("-created_at")[:10]
        
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
        return Response(serializer.data)


class PlatformStatsView(APIView):
    """
    GET /api/platform/stats/
    Top-level counters for the platform-admin dashboard header cards.
    Superuser only.
    """
    permission_classes = [IsSuperUser]

    def get(self, request):
        today = timezone.localdate()
        stats = PlatformService.get_platform_stats(today)
        serializer = PlatformStatSerializer(stats)
        return Response(serializer.data)


class OrganizationGrowthView(APIView):
    """
    GET /api/platform/organization-growth/?months=6
    Monthly count of organizations that reached APPROVED status.
    Superuser only.
    """
    permission_classes = [IsSuperUser]

    def get(self, request):
        try:
            months = int(request.query_params.get("months", 6))
        except ValueError:
            months = 6
        months = max(1, min(months, 24))
        
        today = timezone.localdate()
        growth_data = PlatformService.get_organization_growth(today, months)
        serializer = OrganizationGrowthSerializer(growth_data)
        return Response(serializer.data)


class PlatformActivitiesView(APIView):
    """
    GET /api/platform/activities/?limit=10
    Unified recent-activity feed built from real events.
    Superuser only.
    """
    permission_classes = [IsSuperUser]

    def get(self, request):
        try:
            limit = int(request.query_params.get("limit", 10))
        except ValueError:
            limit = 10
        limit = max(1, min(limit, 50))
        
        activities = PlatformService.get_platform_activities(limit)
        return Response(activities)


class SystemHealthView(APIView):
    """
    GET /api/platform/system-health/
    Best-effort, single-process health snapshot using psutil.
    Superuser only.
    """
    permission_classes = [IsSuperUser]

    def get(self, request):
        health_data = SystemHealthService.get_system_health()
        serializer = SystemHealthSerializer(health_data)
        return Response(serializer.data)
    