from django.db import models

class Assignment(models.Model):
    class_subject = models.ForeignKey('school_admin.ClassSubject', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField()
    CATEGORY_CHOICES = [
        ('cass', 'Continuous Assessment (CASS)'),
        ('exam', 'Examination'),
    ]
    ACTIVITY_TYPE_CHOICES = [
        ('assignment', 'Assignment (Interactive)'),
        ('test', 'Test'),
        ('quiz', 'Quiz'),
        ('exam', 'Examination'),
    ]
    
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='cass', help_text="Weightage Category")
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_TYPE_CHOICES, default='assignment', help_text="Specific type of activity")
    term = models.ForeignKey('school_admin.Term', on_delete=models.SET_NULL, null=True, blank=True, related_name='assignments')
    is_interactive = models.BooleanField(default=True, help_text="If True, students can submit files. If False, score-only.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.class_subject.subject.name} ({self.class_subject.classroom.name})"

class Grade(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='grades')
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='grades_received')
    score = models.DecimalField(max_digits=5, decimal_places=2)
    remarks = models.TextField(blank=True)
    graded_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student.username}: {self.score}/{self.assignment.max_score} for {self.assignment.title}"

class StudentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, limit_choices_to={'role': 'student'}, related_name='submissions')
    submission_file = models.FileField(upload_to='submissions/%Y/%m/%d/', null=True, blank=True)
    submission_link = models.URLField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"Submission by {self.student.get_full_name()} for {self.assignment.title}"

