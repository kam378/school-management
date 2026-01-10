from django import forms
from .models import WhiteboardRoom
from myapps.school_admin.models import GradeLevel, Classroom
from django.contrib.auth import get_user_model

User = get_user_model()

class WhiteboardRoomForm(forms.ModelForm):
    class Meta:
        model = WhiteboardRoom
        fields = ['subject', 'allowed_grade_levels', 'allowed_classrooms', 'students']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Math Class - Linear Algebra'}),
            'allowed_grade_levels': forms.CheckboxSelectMultiple(),
            'allowed_classrooms': forms.CheckboxSelectMultiple(),
            'students': forms.SelectMultiple(attrs={'class': 'form-control select2'}), # Assuming Select2 or standard select
        }
        help_texts = {
            'allowed_grade_levels': 'Select entire grades to allow.',
            'allowed_classrooms': 'Select specific classrooms to allow.',
            'students': 'Select individual students (optional overrides).',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter students to showing only students? Or all users? 
        # Ideally only students. But strict filtering might be heavy if many users.
        self.fields['students'].queryset = User.objects.filter(role='student')
        self.fields['allowed_grade_levels'].queryset = GradeLevel.objects.all()
        self.fields['allowed_classrooms'].queryset = Classroom.objects.all()
