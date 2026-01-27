from django.db import models
from django.conf import settings
from myapps.school_admin.models import GradeLevel, Classroom, Subject

class LearningResource(models.Model):
    RESOURCE_TYPES = [
        ('book', 'E-Book / PDF'),
        ('video', 'Video Lesson'),
        ('document', 'Study Material / Doc'),
        ('link', 'External Reference'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='document')
    
    # Files & Links
    file = models.FileField(upload_to='learning_locker/files/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True, help_text="Link to YouTube, Google Drive, etc.")
    thumbnail = models.ImageField(upload_to='learning_locker/thumbs/', blank=True, null=True)

    # Visibility & Targeting
    is_platform_global = models.BooleanField(
        default=False, 
        help_text="If checked, this item is provided by Super Admin and visible to all students."
    )
    school_wide = models.BooleanField(
        default=False,
        help_text="If checked, every student in this school can see this."
    )
    
    # Specific Targeting (Optional)
    target_levels = models.ManyToManyField(GradeLevel, blank=True, related_name="resources")
    target_classrooms = models.ManyToManyField(Classroom, blank=True, related_name="resources")
    target_subjects = models.ManyToManyField(Subject, blank=True, related_name="resources")

    # Accountability
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="uploaded_resources"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Learning Resource"
        verbose_name_plural = "Learning Resources"

    def __str__(self):
        return self.title
