from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentProfile(models.Model):
    """
    Tenant-specific profile for students containing academic information.
    This avoids putting tenant-specific FKs (GradeLevel, Classroom) on the shared User model.
    """
    student = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    
    grade_level = models.ForeignKey(
        'school_admin.GradeLevel',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='students',
        help_text="Current grade level (e.g., Grade 10)"
    )
    classroom = models.ForeignKey(
        'school_admin.Classroom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrolled_students',
        help_text="Current classroom section"
    )
    
    # Optional: Track academic year entries/exits if needed
    admission_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Profile: {self.student.get_full_name()}"
