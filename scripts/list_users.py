import os
import sys
import django

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from django_tenants.utils import schema_context
from myapps.customers.models import Client
from django.contrib.auth import get_user_model

User = get_user_model()

def list_all_users():
    print("-" * 80)
    print(f"{'TENANT':<15} | {'USERNAME':<15} | {'ROLE':<15} | {'EMAIL':<25} | {'ACTIVE':<5}")
    print("-" * 80)

    # 1. List Public Users (Superadmins usually)
    with schema_context('public'):
        users = User.objects.all()
        for user in users:
            print(f"{'public':<15} | {user.username:<15} | {user.role:<15} | {user.email:<25} | {str(user.is_active):<5}")

    # 2. List Tenant Users
    tenants = Client.objects.all()
    for tenant in tenants:
        if tenant.schema_name == 'public': continue # Already done
        
        with schema_context(tenant.schema_name):
            users = User.objects.all()
            for user in users:
                print(f"{tenant.schema_name:<15} | {user.username:<15} | {user.role:<15} | {user.email:<25} | {str(user.is_active):<5}")

    print("-" * 80)

if __name__ == "__main__":
    list_all_users()
