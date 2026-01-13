from django.db import models

class Assignment(models.Model):
    class_subject = models.ForeignKey('school_admin.ClassSubject', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_score = models.PositiveIntegerField(default=100)
    due_date = models.DateTimeField()
    TYPE_CHOICES = [
        ('cass', 'Continuous Assessment (CASS)'),
        ('exam', 'Examination'),
    ]
    assignment_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='cass', help_text="Categorize as CASS or Exam for weightage")
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

