from django.contrib import admin
from .models import CustomUser, FailedLoginAttempt
from django.contrib.auth.admin import UserAdmin



admin.site.site_header = "My Custom Admin"
admin.site.site_title = "My Admin Portal"
admin.site.index_title = "Welcome to the Admin monitoring Dashboard"

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'username', 'is_custom_admin', 'is_staff', 'is_active')
    list_filter = ('is_custom_admin', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_custom_admin',)}),
    )

@admin.register(FailedLoginAttempt)
class FailedLoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('email', 'password', 'attempt_count', 'timestamp', 'observation')  # Show these fields
    search_fields = ('email',)
    list_filter = ('attempt_count', 'timestamp')

admin.site.register(CustomUser, CustomUserAdmin)

