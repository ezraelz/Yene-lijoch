from django.contrib import admin
from .models import Church


@admin.register(Church)
class ChurchAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'phone',
        'email',
        'created_at',
    )

    search_fields = (
        'name',
        'address',
        'phone',
        'email',
    )

    ordering = ('-created_at',)