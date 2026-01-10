from django import forms
from django.contrib.auth import get_user_model
from .models import ParentProfile

User = get_user_model()

class ParentProfileForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ['children', 'phone_number', 'address']
        widgets = {
            'children': forms.SelectMultiple(attrs={'class': 'form-control', 'style': 'height: 200px;'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. +123456789'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['children'].queryset = User.objects.filter(children_role='student') # Wait, previously filter(role='student')
        self.fields['children'].label_from_instance = lambda obj: f"{obj.get_full_name()} ({obj.custom_id})"

class ParentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class ParentAddressForm(forms.ModelForm):
    class Meta:
        model = ParentProfile
        fields = ['address']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
        }
