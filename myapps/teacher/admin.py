from django.contrib import admin
from .models import Assignment, Grade, StudentSubmission

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'class_subject', 'due_date')
    list_filter = ('class_subject__classroom', 'class_subject__subject')
    search_fields = ('title', 'description')

@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'score', 'graded_at')
    list_filter = ('assignment__class_subject__classroom', 'assignment__class_subject__subject')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'assignment__title')

@admin.register(StudentSubmission)
class StudentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('student', 'assignment', 'submitted_at')
    list_filter = ('assignment__class_subject__classroom', 'assignment__class_subject__subject')
    search_fields = ('student__username', 'student__first_name', 'student__last_name', 'assignment__title')
