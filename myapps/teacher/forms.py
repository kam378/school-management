from django import forms
from .models import Assignment, Grade

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        # Exclude category and is_interactive as they are derived from activity_type
        fields = ['class_subject', 'title', 'activity_type', 'description', 'max_score', 'due_date']
        widgets = {
            'class_subject': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Algebra Quiz 1'}),
            'activity_type': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def save(self, commit=True):
        instance = super(AssignmentForm, self).save(commit=False)
        
        # Auto-configure based on type
        # Exams are separate category
        if instance.activity_type == 'exam':
            instance.category = 'exam'
            instance.is_interactive = False
        # Tests/Quizzes are CASS but non-interactive
        elif instance.activity_type in ['test', 'quiz']:
            instance.category = 'cass'
            instance.is_interactive = False
        # Assignments are CASS and interactive
        else:
            instance.category = 'cass'
            instance.is_interactive = True
            
        # Link current term
        from myapps.school_admin.models import Term
        active_term = Term.objects.filter(is_active=True).first()
        if active_term:
            instance.term = active_term
            
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop('teacher', None)
        super(AssignmentForm, self).__init__(*args, **kwargs)
        if teacher:
            from myapps.school_admin.models import ClassSubject
            self.fields['class_subject'].queryset = ClassSubject.objects.filter(teacher=teacher)


from django.contrib.auth import get_user_model
User = get_user_model()

class TeacherProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
