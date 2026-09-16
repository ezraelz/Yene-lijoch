from django.contrib import admin

from .models import Organization, OrganizationMembership


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "org_type", "status", "created_by", "created_at", "approved_by", "approved_at"]
    list_filter = ["status", "org_type"]
    search_fields = ["name", "normalized_name"]
    readonly_fields = ["normalized_name", "created_at", "approved_at"]


    