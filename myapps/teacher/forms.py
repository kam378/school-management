from django import forms
from .models import Assignment, Grade

class AssignmentForm(forms.ModelForm):
    class Meta:
        model = Assignment
        fields = ['class_subject', 'title', 'description', 'max_score', 'due_date']
        widgets = {
            'class_subject': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Algebra Quiz 1'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'max_score': forms.NumberInput(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

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
