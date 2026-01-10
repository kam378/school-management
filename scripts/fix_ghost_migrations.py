import os
import sys
import django
from django.db import connection

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

def fix_migration_state():
    from django_tenants.utils import tenant_context
    from myapps.customers.models import Client

    print("--- Fixing Migration State ---")
    
    tenants = Client.objects.all()
    
    for tenant in tenants:
        if tenant.schema_name == 'public':
            continue
            
        print(f"\nProcessing tenant: {tenant.schema_name}")
        with tenant_context(tenant):
            with connection.cursor() as cursor:
                cursor.execute(f"DELETE FROM django_migrations;")
                print(f"  Truncated all migration history in {tenant.schema_name}")




    print("\nState cleanup complete. Ready to run migrate_schemas --tenant.")

if __name__ == "__main__":
    fix_migration_state()
