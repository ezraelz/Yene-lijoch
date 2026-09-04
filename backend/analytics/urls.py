from django.urls import path
from . import views

urlpatterns = [
    # Dashboard endpoints
    path('analytics/', views.AnalyticsView.as_view(), name='analytics'),
    path('dashboard/events/', views.DashboardEventsView.as_view(), name='dashboard-events'),
    path('dashboard/activities/', views.DashboardActivitiesView.as_view(), name='dashboard-activities'),
    path('dashboard/performance/', views.DashboardPerformanceView.as_view(), name='dashboard-performance'),
    path('dashboard/announcements/', views.DashboardAnnouncementsView.as_view(), name='dashboard-announcements'),
    
    # Platform admin endpoints
    path('platform/stats/', views.PlatformStatsView.as_view(), name='platform-stats'),
    path('platform/organization-growth/', views.OrganizationGrowthView.as_view(), name='organization-growth'),
    path('platform/activities/', views.PlatformActivitiesView.as_view(), name='platform-activities'),
    path('platform/system-health/', views.SystemHealthView.as_view(), name='system-health'),
]