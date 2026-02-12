from django.contrib import admin
from .models import PasswordEntry, PasswordCategory, PasswordShare, SecurityAudit


@admin.register(PasswordEntry)
class PasswordEntryAdmin(admin.ModelAdmin):
    """Admin interface for PasswordEntry model."""
    
    list_display = [
        'title',
        'user',
        'username_hint',
        'url_hint',
        'category',
        'is_favorite',
        'has_notes',
        'source',
        'created_at',
        'updated_at',
        'last_accessed',
    ]
    list_filter = ['category', 'is_favorite', 'has_notes', 'source', 'created_at', 'updated_at']
    search_fields = ['title', 'username_hint', 'url_hint', 'user__email', 'user__username']
    readonly_fields = [
        'encrypted_data',
        'created_at',
        'updated_at',
        'last_accessed',
        'username_hint',
        'url_hint',
        'has_notes',
    ]
    ordering = ['-created_at']
    list_per_page = 50
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'title', 'username_hint', 'url_hint', 'category')
        }),
        ('Organization', {
            'fields': ('tags', 'is_favorite', 'has_notes')
        }),
        ('Source Information', {
            'fields': ('source', 'source_id'),
            'classes': ('collapse',)
        }),
        ('Encrypted Data', {
            'fields': ('encrypted_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_accessed'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related user."""
        return super().get_queryset(request).select_related('user')


@admin.register(PasswordCategory)
class PasswordCategoryAdmin(admin.ModelAdmin):
    """Admin interface for PasswordCategory model."""
    
    list_display = ['name', 'color', 'icon', 'user', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'user__email']
    readonly_fields = ['created_at']
    ordering = ['name']
    list_per_page = 50
    
    fieldsets = (
        ('Category Information', {
            'fields': ('user', 'name', 'color', 'icon')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related user."""
        return super().get_queryset(request).select_related('user')


@admin.register(PasswordShare)
class PasswordShareAdmin(admin.ModelAdmin):
    """Admin interface for PasswordShare model."""
    
    list_display = [
        'entry',
        'shared_by',
        'shared_with',
        'share_type',
        'is_active',
        'expires_at',
        'created_at',
    ]
    list_filter = ['share_type', 'is_active', 'created_at']
    search_fields = ['entry__title', 'shared_by__email', 'shared_with__email']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    list_per_page = 50
    
    fieldsets = (
        ('Share Information', {
            'fields': ('entry', 'shared_by', 'shared_with', 'share_type', 'message')
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related models."""
        return super().get_queryset(request).select_related('entry', 'shared_by', 'shared_with')


@admin.register(SecurityAudit)
class SecurityAuditAdmin(admin.ModelAdmin):
    """Admin interface for SecurityAudit model."""
    
    list_display = [
        'user',
        'event_type',
        'entry',
        'ip_address',
        'timestamp',
    ]
    list_filter = ['event_type', 'timestamp']
    search_fields = ['user__email', 'entry__title', 'ip_address']
    readonly_fields = ['timestamp', 'event_type', 'user', 'entry', 'ip_address', 'user_agent', 'details']
    ordering = ['-timestamp']
    list_per_page = 100
    
    fieldsets = (
        ('Event Information', {
            'fields': ('user', 'event_type', 'entry')
        }),
        ('Request Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Additional Details', {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('timestamp',),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with related models."""
        return super().get_queryset(request).select_related('user', 'entry')
