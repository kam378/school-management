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
