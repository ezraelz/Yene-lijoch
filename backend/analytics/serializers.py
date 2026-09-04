from rest_framework import serializers


class EventSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    date = serializers.CharField()
    time = serializers.CharField(required=False, allow_blank=True)
    location = serializers.CharField(required=False, allow_null=True)
    type = serializers.CharField(default="school")
    description = serializers.CharField(required=False, allow_blank=True)


class ActivitySerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    createdAt = serializers.CharField()
    user = serializers.CharField(allow_null=True)


class AnnouncementSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField()
    createdAt = serializers.CharField()
    type = serializers.CharField()


class PerformanceIndicatorSerializer(serializers.Serializer):
    label = serializers.CharField()
    value = serializers.FloatField()
    target = serializers.IntegerField()


class PlatformStatSerializer(serializers.Serializer):
    totalOrganizations = serializers.IntegerField()
    approvedOrganizations = serializers.IntegerField()
    pendingOrganizations = serializers.IntegerField()
    totalUsers = serializers.IntegerField()
    growth = serializers.FloatField()
    pendingApprovals = serializers.IntegerField()
    activeSubscriptions = serializers.IntegerField(allow_null=True)
    revenue = serializers.FloatField(allow_null=True)


class OrganizationGrowthSerializer(serializers.Serializer):
    labels = serializers.ListField(child=serializers.CharField())
    values = serializers.ListField(child=serializers.IntegerField())
    growth = serializers.FloatField()


class SystemHealthSerializer(serializers.Serializer):
    status = serializers.CharField()
    uptime = serializers.CharField()
    responseTime = serializers.FloatField()
    serverLoad = serializers.FloatField(allow_null=True)
    memoryPercent = serializers.FloatField(allow_null=True)
    activeJobs = serializers.IntegerField(allow_null=True)
    note = serializers.CharField(required=False, allow_null=True)
    