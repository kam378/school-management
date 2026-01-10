
import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context
from myapps.customers.models import Client

def create_tenant_superuser(schema_name, username, email, password):
    try:
        tenant = Client.objects.get(schema_name=schema_name)
        with schema_context(schema_name):
            User = get_user_model()
            if not User.objects.filter(username=username).exists():
                User.objects.create_superuser(username=username, email=email, password=password, role='school_admin')
                print(f"Superuser '{username}' created for tenant '{schema_name}'.")
            else:
                print(f"Superuser '{username}' already exists in tenant '{schema_name}'.")
    except Client.DoesNotExist:
        print(f"Tenant with schema '{schema_name}' does not exist.")

if __name__ == "__main__":
    # Create superusers for each tenant
    create_tenant_superuser('school_a', 'admin_a', 'admin_a@school.com', 'admin_a_pass')
    create_tenant_superuser('school_b', 'admin_b', 'admin_b@school.com', 'admin_b_pass')
    create_tenant_superuser('demo_school_two', 'admin_demo', 'admin_demo@school.com', 'admin_demo_pass')
    
    print("\nSuperuser creation complete.")
