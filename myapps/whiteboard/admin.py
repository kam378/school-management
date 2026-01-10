from django.contrib import admin
from .models import WhiteboardRoom

# Register your models here.

@admin.register(WhiteboardRoom)
class WhiteboardRoomAdmin(admin.ModelAdmin):
    list_display = ('short_code', 'teacher_display', 'subject', 'created_at')
    search_fields = ('short_code', 'subject', 'teacher__email')
    ordering = ('-created_at',)  # admin sees newest rooms first
    list_filter = ('subject', 'created_at', 'teacher')
    
    def teacher_display(self, obj):
      return obj.teacher.email if obj.teacher else "Deleted Teacher"  # if the teacher account is deleted will show "deleted teacher"
    teacher_display.short_description = 'Teacher'  # This is what appears as the column header in the admin list.

