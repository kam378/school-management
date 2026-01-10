from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
class Client(TenantMixin):
  name = models.CharField(max_length=100)
  subscription_plan = models.ForeignKey('super_admin.SubscriptionPlan', on_delete=models.SET_NULL, null=True, blank=True)
  created_on = models.DateField(auto_now_add=True)

  auto_create_schema = True
  def __str__(self):
      return self.name

class Domain(DomainMixin):
  pass