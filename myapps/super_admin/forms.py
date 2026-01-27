from django import forms
from myapps.customers.models import Client, Domain
from .models import SubscriptionPlan, GlobalSetting

class GlobalSettingsForm(forms.ModelForm):
    class Meta:
        model = GlobalSetting
        fields = ['platform_name', 'logo', 'primary_color', 'is_dark_mode']
        widgets = {
            'platform_name': forms.TextInput(attrs={'class': 'form-control'}),
            'primary_color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }




class TenantForm(forms.ModelForm):
    domain_name = forms.CharField(max_length=128, label="Domain Name (e.g. school-unique.localhost)")

    class Meta:
        model = Client
        fields = ['name', 'schema_name', 'subscription_plan']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'School Name'}),
            'schema_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'schema_name (lowercase, no spaces)'}),
            'subscription_plan': forms.Select(attrs={'class': 'form-control'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['domain_name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'school-unique.localhost'})

        if self.instance.pk:
            # If editing, try to get the primary domain
            primary_domain = self.instance.domains.filter(is_primary=True).first()
            if primary_domain:
                self.fields['domain_name'].initial = primary_domain.domain

class DomainForm(forms.ModelForm):
    class Meta:
        model = Domain
        fields = ['domain', 'is_primary']
        widgets = {
            'domain': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'domain.example.com'}),
        }

class SubscriptionPlanForm(forms.ModelForm):
    class Meta:
        model = SubscriptionPlan
        fields = ['name', 'max_students', 'max_teachers', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Plan Name'}),
            'max_students': forms.NumberInput(attrs={'class': 'form-control'}),
            'max_teachers': forms.NumberInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

from .models import PlatformResource

class PlatformResourceForm(forms.ModelForm):
    class Meta:
        model = PlatformResource
        fields = ['title', 'description', 'resource_type', 'file', 'external_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Global Book Title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resource_type': forms.Select(attrs={'class': 'form-control'}),
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'external_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://...'}),
        }


