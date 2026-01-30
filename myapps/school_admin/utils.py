from myapps.core.models import Notification

def get_notifications(user):
    return Notification.objects.filter(user=user, is_read=False).count()

def log_action(user, action, target_model, target_id=None, details="", request=None):
    from django.db import connection
    
    ip = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

    if connection.schema_name == 'public':
        from myapps.super_admin.models import PlatformAuditLog
        LogModel = PlatformAuditLog
    else:
        from .models import AuditLog
        LogModel = AuditLog

    LogModel.objects.create(
        user=user,
        action=action,
        target_model=target_model,
        target_id=str(target_id) if target_id else None,
        details=details,
        ip_address=ip
    )