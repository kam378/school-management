import os
import sys
import django
from django.db import connection

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

def verify_isolation():
    from django_tenants.utils import tenant_context
    from myapps.customers.models import Client
    from django.contrib.auth import get_user_model
    User = get_user_model()

    print("--- Final Isolation Verification ---")
    
    tenants = Client.objects.all()
    for tenant in tenants:
        if tenant.schema_name == 'public':
            print(f"\nPublic Schema:")
            with connection.cursor() as cursor:
                cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public' AND tablename = 'accounts_user';")
                if cursor.fetchone():
                    print("  [ERROR] accounts_user still exists in public schema!")
                else:
                    print("  [OK] accounts_user does not exist in public schema.")
            continue
            
        print(f"\nTenant Schema: {tenant.schema_name}")
        with tenant_context(tenant):
            # Try to count users
            try:
                count = User.objects.count()
                print(f"  [OK] User model accessible. Count: {count}")
            except Exception as e:
                print(f"  [ERROR] User model NOT accessible: {e}")
            
            # Check table directly
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = '{tenant.schema_name}' AND tablename = 'accounts_user';")
                if cursor.fetchone():
                    print("  [OK] accounts_user table exists.")
                else:
                    print(f"  [ERROR] accounts_user table MISSING in {tenant.schema_name}!")

if __name__ == "__main__":
    verify_isolation()
