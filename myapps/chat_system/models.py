from django.conf import settings
from django.db import models

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username}: {self.content[:20]}"
    
    class Meta:
        ordering = ['timestamp']
