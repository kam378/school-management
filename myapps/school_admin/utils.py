from myapps.core.models import Notification

def get_notifications(user):
  return Notification.objects.filter(user=user, is_read=False).count()