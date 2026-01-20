from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from .models import GradeLevel, Subject, Classroom, ClassSubject, Timetable, SchoolSettings, Announcement, CalendarEvent, GradeScale, AcademicYear, Term
from myapps.accounts.models import User

class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['name', 'start_date', 'end_date', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2024-2025'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TermForm(forms.ModelForm):
    class Meta:
        model = Term
        fields = ['name', 'academic_year', 'start_date', 'end_date', 'is_active', 'is_published']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Term 1'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class GradeScaleForm(forms.ModelForm):
    class Meta:
        model = GradeScale
        fields = ['label', 'min_percentage', 'grade_point', 'color_code']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. A, B+, C'}),
            'min_percentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'grade_point': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'color_code': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }

class AdminSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super(AdminSetPasswordForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = f'Enter {field.label.lower()}'

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'first_name', 'last_name', 'email')
    
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        # Apply form-control class to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'password1':
                field.widget.attrs['placeholder'] = 'Minimum 8 characters'
            elif field_name == 'password2':
                field.widget.attrs['placeholder'] = 'Re-enter password'



class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'birth_date', 'role', 'is_active')

class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'body', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
        }

class GradeLevelForm(forms.ModelForm):
    class Meta:
        model = GradeLevel
        fields = ['name', 'subjects']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'subjects': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
        }


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ClassroomForm(forms.ModelForm):
    class Meta:
        model = Classroom
        fields = ['name', 'level', 'homeroom_teacher', 'students']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'level': forms.Select(attrs={'class': 'form-control'}),
            'homeroom_teacher': forms.Select(attrs={'class': 'form-control'}),
            'students': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class ClassSubjectForm(forms.ModelForm):
    class Meta:
        model = ClassSubject
        fields = ['classroom', 'subject', 'teacher']
        widgets = {
            'classroom': forms.Select(attrs={'class': 'form-control', 'onchange': 'this.form.submit()'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'teacher': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        classroom_id = kwargs.pop('classroom_id', None)
        super(ClassSubjectForm, self).__init__(*args, **kwargs)
        if classroom_id:
            try:
                classroom = Classroom.objects.get(id=classroom_id)
                self.fields['subject'].queryset = classroom.level.subjects.all()
                self.initial['classroom'] = classroom
            except Classroom.DoesNotExist:
                pass


class TimetableForm(forms.ModelForm):
    class Meta:
        model = Timetable
        fields = ['class_subject', 'day', 'start_time', 'end_time', 'room_number']
        widgets = {
            'class_subject': forms.Select(attrs={'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['title', 'description', 'start_date', 'end_date', 'event_type']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Event Description', 'rows': 3}),
            'start_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
        }

class SchoolSettingsForm(forms.ModelForm):
    class Meta:
        model = SchoolSettings
        fields = ['school_name', 'address', 'email', 'phone', 
                  'enable_whiteboard', 'enable_chat', 'enable_attendance',
                  'primary_color', 'secondary_color', 'is_dark_mode', 'logo',
                  'cass_weight', 'exam_weight']
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'cass_weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'exam_weight': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class AdminProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

from myapps.student.models import StudentProfile

class StudentProfileAdminForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['grade_level', 'classroom', 'admission_date']
        widgets = {
            'grade_level': forms.Select(attrs={'class': 'form-control'}),
            'classroom': forms.Select(attrs={'class': 'form-control'}),
            'admission_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
from myapps.parent.models import ParentProfile

class ParentProfileAdminForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ['phone_number', 'address']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
