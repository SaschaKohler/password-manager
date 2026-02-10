from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserSession, SecurityLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'totp_enabled', 'failed_login_attempts', 'is_active')
    list_filter = ('totp_enabled', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('email', 'username')
    ordering = ('email',)
    
    fieldsets = (
        (None, {
            'fields': ('email', 'username', 'password')
        }),
        ('Security', {
            'fields': (
                'master_password_hash', 'master_password_salt', 'encryption_key',
                'totp_secret', 'totp_enabled', 'backup_codes',
                'last_password_change', 'failed_login_attempts', 'locked_until'
            )
        }),
        ('Preferences', {
            'fields': ('password_generator_length', 'password_generator_symbols')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    readonly_fields = (
        'master_password_hash', 'master_password_salt', 'encryption_key',
        'totp_secret', 'backup_codes', 'last_password_change',
        'failed_login_attempts', 'locked_until'
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at', 'last_activity', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('user__email', 'ip_address')
    readonly_fields = ('session_key', 'user_agent', 'created_at', 'last_activity')


@admin.register(SecurityLog)
class SecurityLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'event_type', 'ip_address', 'timestamp')
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__email', 'description')
    readonly_fields = ('user', 'event_type', 'ip_address', 'user_agent', 'description', 'timestamp')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
