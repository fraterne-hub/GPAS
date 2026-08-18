from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserPreference, AuditLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display    = ('email', 'username', 'get_full_name', 'role', 'is_active', 'is_verified', 'date_joined')
    list_filter     = ('role', 'is_active', 'is_staff', 'is_verified')
    search_fields   = ('email', 'username', 'first_name', 'last_name')
    ordering        = ('-date_joined',)
    fieldsets = (
        (None,           {'fields': ('email', 'password')}),
        (_('Personal'),  {'fields': ('first_name', 'last_name', 'username')}),
        (_('Role'),      {'fields': ('role',)}),
        (_('Status'),    {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        (_('Permissions'),{'fields': ('groups', 'user_permissions')}),
        (_('Dates'),     {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display    = ('user', 'country', 'institution', 'visibility')
    search_fields   = ('user__email', 'user__username', 'institution')
    list_filter     = ('visibility', 'country')


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'theme', 'language', 'email_notifications')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display    = ('user', 'action', 'model_name', 'object_repr', 'ip_address', 'timestamp')
    list_filter     = ('action', 'model_name')
    search_fields   = ('user__email', 'description', 'object_repr')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'object_repr',
                       'description', 'ip_address', 'user_agent', 'timestamp', 'extra_data')
    ordering        = ('-timestamp',)
