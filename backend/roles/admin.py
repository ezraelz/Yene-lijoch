from django.contrib import admin
from .models import Role

class RoleAdmin(admin.ModelAdmin):
    list_display = ["id", "role_name", "is_active", "created_at"]

admin.site.register(Role, RoleAdmin)