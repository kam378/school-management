from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# Create your models here.

class Announcement(models.Model):
    title = models.CharField(max_length=255, blank=True)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    author = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.title} posted by {self.author}"

class SchoolSettings(models.Model):
    school_name = models.CharField(max_length=255, default="EduManage High School")
    address = models.TextField(default="123 Education Lane, Knowledge City")
    email = models.EmailField(default="contact@edumanage.com")
    phone = models.CharField(max_length=50, default="+1 234 567 890")
    
    # Feature Toggles
    enable_whiteboard = models.BooleanField(default=True)
    enable_chat = models.BooleanField(default=True)
    enable_attendance = models.BooleanField(default=True)
    
    # Theme Settings
    primary_color = models.CharField(max_length=20, default="#4a90e2")
    secondary_color = models.CharField(max_length=20, default="#2c3e50")
    is_dark_mode = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='school_logos/', blank=True, null=True)
    # Grading Settings
    cass_weight = models.PositiveIntegerField(default=40, help_text="Weight percentage for Continuous Assessment (0-100)")
    exam_weight = models.PositiveIntegerField(default=60, help_text="Weight percentage for Exams (0-100)")
    
    def save(self, *args, **kwargs):
        if not self.pk and SchoolSettings.objects.exists():
            # If you try to save a new instance, but one exists, update the existing one
            return SchoolSettings.objects.first()
        # Ensure weights add up to 100 or handle validation? 
        # For now, we'll just allow setting them.
        return super(SchoolSettings, self).save(*args, **kwargs)

    def __str__(self):
        return "School Settings"

class AcademicYear(models.Model):
    name = models.CharField(max_length=50, help_text="e.g. 2024-2025")
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False, help_text="Set as current academic year")
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate other years
            AcademicYear.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Term(models.Model):
    name = models.CharField(max_length=50, help_text="e.g. First Term")
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE, related_name='terms')
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=False, help_text="Set as current active term for new data")
    is_published = models.BooleanField(default=False, help_text="If checked, students can view results for this term")

    def save(self, *args, **kwargs):
        if self.is_active:
            # Deactivate other terms
            Term.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.academic_year.name})"

class GradeScale(models.Model):
    """Custom grading scale defined by the school admin"""
    label = models.CharField(max_length=10, help_text="e.g., A, B+, C")
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Minimum percentage required for this grade")
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, help_text="GP value (e.g., 4.0)")
    color_code = models.CharField(max_length=20, default="#1e293b", help_text="Hex color for UI badges")

    class Meta:
        ordering = ['-min_percentage']
        verbose_name = "Grade Scale"
        verbose_name_plural = "Grade Scales"

    def __str__(self):
        return f"{self.label} ({self.min_percentage}%)"

class GradeLevel(models.Model):
    name = models.CharField(max_length=50)
    subjects = models.ManyToManyField('Subject', related_name='grade_levels', blank=True)

    def __str__(self):

        return self.name

class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    name = models.CharField(max_length=50)
    level = models.ForeignKey(GradeLevel, on_delete=models.CASCADE, related_name='classrooms')
    students = models.ManyToManyField('accounts.User', limit_choices_to={'role': 'student'}, related_name='classrooms_enrolled', blank=True)
    homeroom_teacher = models.ForeignKey(
        'accounts.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'teacher'},
        related_name='homeroom_class',
        help_text="Form teacher responsible for this class"
    )

    def __str__(self):
        return f"{self.name} ({self.level.name})"

class ClassSubject(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'teacher'}, related_name='assigned_subjects')

    class Meta:
        unique_together = ('classroom', 'subject')

    def __str__(self):
        return f"{self.subject.name} - {self.classroom.name} ({self.teacher.get_full_name() if self.teacher else 'No Teacher'})"

class Timetable(models.Model):
    DAYS_OF_WEEK = [
        (1, 'Monday'),
        (2, 'Tuesday'),
        (3, 'Wednesday'),
        (4, 'Thursday'),
        (5, 'Friday'),
        (6, 'Saturday'),
        (7, 'Sunday'),
    ]

    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='timetable_slots')
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    room_number = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        ordering = ['day', 'start_time']

    def __str__(self):
        return f"{self.class_subject.subject.name} - {self.get_day_display()} at {self.start_time}"


class PromotionRecord(models.Model):
    """Audit trail for student grade promotions"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promotion_history')
    from_grade = models.ForeignKey(GradeLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions_from')
    to_grade = models.ForeignKey(GradeLevel, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions_to')
    from_classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions_from')
    to_classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True, related_name='promotions_to')
    promoted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='promotions_performed')
    promotion_date = models.DateTimeField(auto_now_add=True)
    academic_year = models.CharField(max_length=20, help_text="e.g., 2024-2025")
    notes = models.TextField(blank=True, help_text="Optional notes about this promotion")
    
    class Meta:
        ordering = ['-promotion_date']
    
    def __str__(self):
        return f"{self.student.get_full_name()} promoted from {self.from_grade} to {self.to_grade}"


class CalendarEvent(models.Model):
    EVENT_TYPES = [
        ('event', 'General Event'),
        ('holiday', 'Holiday'),
        ('exam', 'Examination'),
        ('meeting', 'Meeting'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='event')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='calendar_events')

    class Meta:
        ordering = ['start_date']
        verbose_name = "School Calendar Event"
        verbose_name_plural = "School Calendar Events"

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"


class AuditLog(models.Model):
    """Audit logs for actions performed within a specific school (tenant)"""
    from myapps.accounts.models import AUDIT_ACTION_CHOICES

    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=AUDIT_ACTION_CHOICES)
    target_model = models.CharField(max_length=100)
    target_id = models.CharField(max_length=100, blank=True, null=True)
    details = models.TextField(blank=True, help_text="JSON or text representation of changes")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['action']),
        ]

    def __str__(self):
        return f"{self.action} on {self.target_model} by {self.user} at {self.timestamp}"
