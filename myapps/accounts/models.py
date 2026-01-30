from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime
# from myapps.school_admin.models import GradeLevel, Classroom

AUDIT_ACTION_CHOICES = [
    ('CREATE', 'Created'),
    ('UPDATE', 'Updated'),
    ('DELETE', 'Deleted'),
    ('PROMOTION', 'Student Promotion'),
    ('SETTINGS', 'Settings Changed'),
    ('SECURITY', 'Security Event'),
    ('THROTTLE', 'IP Throttled'),
]

class User(AbstractUser):
    ROLE_CHOICES = [
        ('school_admin', 'School Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
        ('parent', 'Parent'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    custom_id = models.CharField(max_length=50, unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    # Login security
    failed_login_attempts = models.PositiveIntegerField(default=0)
    lockout_until = models.DateTimeField(null=True, blank=True)


    def save(self, *args, **kwargs):
        # Only generate ID if it doesn't exist yet
        if not self.custom_id:
            # 1. Get the prefix based on role
            prefix_map = {
                'school_admin': 'A',
                'teacher': 'T',
                'student': 'S',
                'parent': 'P'
            }
            prefix = prefix_map.get(self.role, 'U')
            
            # 2. Get current year
            year = datetime.now().year
            
            # 3. Find the last used ID for this role & year
            # We filter by role and year, then order by custom_id descending to get the highest one.
            last_user = User.objects.filter(
                role=self.role, 
                date_joined__year=year
            ).order_by('-custom_id').first()
            if last_user and last_user.custom_id:
                try:
                    # Extract the sequence number (last 3 digits)
                    last_sequence = int(last_user.custom_id.split('-')[-1])
                    sequence = last_sequence + 1
                except (ValueError, IndexError):
                    sequence = 1
            else:
                sequence = 1
            
            # 4. Format: P-2023-001
            # Loop check to handle race conditions (rare but safer)
            while True:
                new_id = f"{prefix}-{year}-{sequence:03d}"
                if not User.objects.filter(custom_id=new_id).exists():
                    self.custom_id = new_id
                    break
                sequence += 1
            
        super().save(*args, **kwargs)

    def is_school_admin(self):
        return self.role == 'school_admin'

    def is_teacher(self):
        return self.role == 'teacher'

    def is_student(self):
        return self.role == 'student'

    def is_parent(self):
        return self.role == 'parent'

