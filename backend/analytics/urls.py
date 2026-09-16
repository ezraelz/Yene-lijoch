from django.urls import path
from .views import (
    AnalyticsView,
    DashboardEventsView,
    DashboardActivitiesView,
    DashboardPerformanceView,
    DashboardAnnouncementsView,
    PlatformStatsView,
    OrganizationGrowthView,
    PlatformActivitiesView,
    SystemHealthView,
)

urlpatterns = [
    # Dashboard
    path("analytics/", AnalyticsView.as_view(), name="analytics"),
    path("dashboard/events/", DashboardEventsView.as_view(), name="dashboard-events"),
    path("dashboard/activities/", DashboardActivitiesView.as_view(), name="dashboard-activities"),
    path("dashboard/performance/", DashboardPerformanceView.as_view(), name="dashboard-performance"),
    path("dashboard/announcements/", DashboardAnnouncementsView.as_view(), name="dashboard-announcements"),

    # Platform
    path("api/platform/stats/", PlatformStatsView.as_view(), name="platform-stats"),
    path("api/platform/organization-growth/", OrganizationGrowthView.as_view(), name="platform-org-growth"),
    path("api/platform/activities/", PlatformActivitiesView.as_view(), name="platform-activities"),
    path("api/platform/system-health/", SystemHealthView.as_view(), name="platform-system-health"),
]
