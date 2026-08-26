# admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Church

@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'denomination', 
        'status_colored', 
        'pastor', 
        'total_members',
        'region',
        'created_at'
    )
    list_filter = ('status', 'denomination', 'region', 'created_at')
    search_fields = ('name', 'address', 'pastor', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'denomination', 'status', 'is_approved')
        }),
        ('Contact Information', {
            'fields': ('address', 'region', 'phone', 'email', 'website')
        }),
        ('Leadership & Statistics', {
            'fields': ('pastor', 'founded', 'total_members', 'total_services')
        }),
        ('Service Times', {
            'fields': ('service_times',),
            'classes': ('collapse',),
            'description': 'Enter service times in JSON format: {"sunday": "10:00 AM", "wednesday": "7:00 PM"}'
        }),
        ('Social Media', {
            'fields': ('social_media',),
            'classes': ('collapse',),
            'description': 'Enter social media URLs in JSON format: {"facebook": "https://facebook.com/church"}'
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def status_colored(self, obj):
        """Display status with color coding"""
        colors = {
            'active': 'green',
            'inactive': 'red',
            'pending': 'orange'
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_colored.short_description = 'Status'
    
    actions = ['mark_as_active', 'mark_as_inactive', 'mark_as_pending']
    
    def mark_as_active(self, request, queryset):
        queryset.update(status='active')
    mark_as_active.short_description = "Mark selected churches as Active"
    
    def mark_as_inactive(self, request, queryset):
        queryset.update(status='inactive')
    mark_as_inactive.short_description = "Mark selected churches as Inactive"
    
    def mark_as_pending(self, request, queryset):
        queryset.update(status='pending')
    mark_as_pending.short_description = "Mark selected churches as Pending"
