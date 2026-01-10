from django.db import models
from django.conf import settings
from .agora import create_room

# Create your models here.

class WhiteboardRoom(models.Model):
  teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='whiteboard_rooms')
  # We store the *Real* Agora Room UUID here.
  room_uuid = models.CharField(max_length=128, unique=True, blank=True) 
  short_code = models.CharField(max_length=10, unique=True)
  subject = models.CharField(max_length=100, blank=False)
  created_at = models.DateTimeField(auto_now_add=True)
  
  # add enrolled students
  students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='enrolled_whiteboard_rooms', blank=True)
  
  # Bulk Assignment
  allowed_grade_levels = models.ManyToManyField('school_admin.GradeLevel', related_name='whiteboard_rooms', blank=True)
  allowed_classrooms = models.ManyToManyField('school_admin.Classroom', related_name='whiteboard_rooms', blank=True)

  def save(self, *args, **kwargs):
      # If this is a new room (no UUID yet), create it on Agora
      if not self.room_uuid:
          try:
              external_uuid = create_room(name=self.subject, limit=0)
              self.room_uuid = external_uuid
          except Exception as e:
              # In a real app, you might want to log this or handle it gracefully
              # For now, we allow the save but the room might be broken or we re-raise
              print(f"Error creating Agora Room: {e}")
              raise e
      super().save(*args, **kwargs)

  def __str__(self):
    return f"{self.subject} ({self.short_code})"

