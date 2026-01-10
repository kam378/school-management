from django.db import models
from django.conf import settings

class ParentProfile(models.Model):
    """
    Profile for parent users, linking them to one or more student users.
    """
    parent = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='parent_profile',
        limit_choices_to={'role': 'parent'}
    )
    children = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='parents',
        limit_choices_to={'role': 'student'},
        blank=True
    )
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Parent: {self.parent.get_full_name()}"
