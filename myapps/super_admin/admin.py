from django.contrib import admin
from .models import SubscriptionPlan, GlobalSetting, PlatformResource, PlatformAuditLog

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_students', 'max_teachers', 'price')
    search_fields = ('name',)

@admin.register(GlobalSetting)
class GlobalSettingAdmin(admin.ModelAdmin):
    list_display = ('platform_name', 'maintenance_mode', 'is_dark_mode', 'updated_at')
    list_editable = ('maintenance_mode', 'is_dark_mode')

@admin.register(PlatformResource)
class PlatformResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'resource_type', 'created_at')
    list_filter = ('resource_type', 'created_at')
    search_fields = ('title', 'description')

@admin.register(PlatformAuditLog)
class PlatformAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'user', 'target_model', 'ip_address')
    list_filter = ('action', 'target_model', 'timestamp')
    search_fields = ('user__username', 'details', 'target_id')
    readonly_fields = ('timestamp',)

    def has_add_permission(self, request):
        return False  # Logs should be system-generated

    def has_change_permission(self, request, obj=None):
        return False  # Logs should not be edited

    def has_delete_permission(self, request, obj=None):
        return False  # Logs should not be deleted for audit integrity
