from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Profile

class ProfileAdmin(UserAdmin):
    model = Profile
    list_display = ('id','email', 'username', 'role', 
                    'is_active','profile_image',
                      'is_staff', 'is_superuser','address',
                      )
    list_filter = ('role', 'is_active', 'is_staff')
    fieldsets = (
        (None, {
            'fields': ('first_name','last_name',
                       'username','age', 'sex', 'email',
                         'role','last_seen','profile_image',
                           'is_staff', 'is_superuser', 'contact',
                           'is_active','address', 'bio', 'password')
        }),
    )
    readonly_fields = ['last_seen', 'password']
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(Profile, ProfileAdmin)

