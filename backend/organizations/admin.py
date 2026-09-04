from django.contrib import admin

from .models import Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "org_type", "status", "created_by", "created_at", "approved_by", "approved_at"]
    list_filter = ["status", "org_type"]
    search_fields = ["name", "normalized_name"]
    readonly_fields = ["normalized_name", "created_at", "approved_at"]


@admin.register(OrganizationMembership)
class OrganizationMembershipAdmin(admin.ModelAdmin):
    list_display = ["user", "organization", "role", "status", "requested_at", "reviewed_by", "reviewed_at"]
    list_filter = ["status", "role"]
    search_fields = ["user__username", "organization__name"]
    