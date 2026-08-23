from django.contrib import admin
from .models import Church


@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'phone',
        'email',
        'status',
        'created_at',
    )

    search_fields = (
        'name',
        'address',
        'phone',
        'email',
        'status',
    )

    ordering = ('-created_at',)