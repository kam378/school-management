from django.db import models
from django.urls import reverse

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    max_students = models.PositiveIntegerField(default=100)
    max_teachers = models.PositiveIntegerField(default=20)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    class Meta:
        verbose_name = "Subscription Plan"
        verbose_name_plural = "Subscription Plans"

    def __str__(self):
        return f"{self.name} (Max: {self.max_students} Students)"

class GlobalSetting(models.Model):
    maintenance_mode = models.BooleanField(default=False)
    platform_name = models.CharField(max_length=100, default="EduManage")
    logo = models.ImageField(upload_to='system_logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=7, default="#4a90e2")
    is_dark_mode = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name_plural = "Global Settings"

    def __str__(self):
        return f"Global Settings (Maintenance: {self.maintenance_mode})"

    @classmethod
    def is_maintenance_active(cls):
        from django_tenants.utils import schema_context
        with schema_context('public'):
            obj, created = cls.objects.get_or_create(pk=1)
            return obj.maintenance_mode

class PlatformResource(models.Model):
    RESOURCE_TYPES = [
        ('book', 'E-Book / PDF'),
        ('video', 'Video Lesson'),
        ('document', 'Study Material / Doc'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, default='book')
    file = models.FileField(upload_to='platform_resources/files/', blank=True, null=True)
    external_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Platform Global Resource"
        verbose_name_plural = "Platform Global Resources"

    def __str__(self):
        return f"[GLOBAL] {self.title}"
