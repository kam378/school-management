from django.contrib import admin
from .models import Announcement, SchoolSettings, GradeScale, AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'action', 'user', 'target_model', 'ip_address')
    list_filter = ('action', 'target_model')
    search_fields = ('user__username', 'details', 'target_id')
    readonly_fields = ('timestamp', 'user', 'action', 'target_model', 'target_id', 'details', 'ip_address')

# Register your models here.
admin.site.register(Announcement)
admin.site.register(SchoolSettings)
admin.site.register(GradeScale)