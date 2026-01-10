import os
import sys
import django
from django.db import connection

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

def thorough_cleanup():
    from myapps.customers.models import Client, Domain

    print("--- Starting Thorough Tenant Cleanup ---")
    
    # 1. Store existing tenants (except public if it's there)
    tenants_data = []
    for client in Client.objects.all():
        if client.schema_name == 'public':
            continue
        
        domain = Domain.objects.filter(tenant=client).first()
        tenants_data.append({
            'name': client.name,
            'schema_name': client.schema_name,
            'domain': domain.domain if domain else f"{client.schema_name}.localhost"
        })
    
    print(f"Captured data for {len(tenants_data)} tenants.")

    # 2. Delete all domains and clients (Drops schemas)
    print("Deleting existing domains and clients...")
    Domain.objects.all().delete()
    Client.objects.all().delete()
    print("Deleted.")

    # 3. Clean up Public Schema (Delete orphan tables)
    print("\nCleaning up public schema orphan tables...")
    public_tables_to_drop = [
        'accounts_user_user_permissions',
        'accounts_user_groups',
        'accounts_user',
        'core_notification',
        'django_admin_log',
        'django_session'
    ]
    
    with connection.cursor() as cursor:
        for table in public_tables_to_drop:
            try:
                print(f"  Dropping public.{table}...")
                cursor.execute(f"DROP TABLE IF EXISTS public.{table} CASCADE;")
            except Exception as e:
                print(f"  Error dropping {table}: {e}")
                
        # Also clean up migration history in public for apps that moved
        apps_that_moved = ['accounts', 'core', 'admin', 'sessions']
        for app in apps_that_moved:
            try:
                print(f"  Removing public migration history for {app}...")
                cursor.execute(f"DELETE FROM public.django_migrations WHERE app = '{app}';")
            except Exception as e:
                print(f"  Error clearing migration for {app}: {e}")

    # 4. Re-create tenants one by one
    print("\nRe-creating tenants (this will run migrations for each)...")
    for data in tenants_data:
        print(f"  Creating {data['name']} ({data['schema_name']})...")
        tenant = Client(schema_name=data['schema_name'], name=data['name'])
        tenant.save()
        
        Domain.objects.create(
            domain=data['domain'],
            tenant=tenant,
            is_primary=True
        )
        print(f"  Created.")

    print("\n--- Cleanup and Re-creation Complete! ---")
    print("All users are now isolated in their respective tenant schemas.")
    print("The public schema is clean.")

if __name__ == "__main__":
    thorough_cleanup()
