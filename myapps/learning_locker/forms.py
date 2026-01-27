from django import forms
from .models import LearningResource

class LearningResourceForm(forms.ModelForm):
    class Meta:
        model = LearningResource
        fields = [
            'title', 'description', 'resource_type', 'file', 
            'external_url', 'thumbnail', 'is_platform_global', 'school_wide',
            'target_levels', 'target_classrooms', 'target_subjects'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_platform_global': forms.CheckboxInput(),
            'school_wide': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # If user is a teacher, prevent them from setting 'is_platform_global'
        if user and not user.is_school_admin() and not user.is_superuser:
            if 'is_platform_global' in self.fields:
                self.fields['is_platform_global'].disabled = True
                self.fields['is_platform_global'].widget = forms.HiddenInput()
            if 'school_wide' in self.fields:
                self.fields['school_wide'].disabled = True
                self.fields['school_wide'].widget = forms.HiddenInput()
