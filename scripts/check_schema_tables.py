import os
import sys
import django
from django.db import connection

# Add the project root to sys.path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

def check_tables():
    from django_tenants.utils import tenant_context
    from myapps.customers.models import Client

    print("--- Public Schema Tables ---")
    with connection.cursor() as cursor:
        cursor.execute("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = 'public';")
        tables = cursor.fetchall()
        for t in tables:
            print(f"  {t[0]}")

    tenants = Client.objects.filter(schema_name='school_a')
    for tenant in tenants:
        print(f"\n--- ALL Migrations in ({tenant.schema_name}) ---")
        with tenant_context(tenant):
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT app, name FROM django_migrations ORDER BY app, name;")
                migrations = cursor.fetchall()
                for m in migrations:
                    print(f"  {m[0]}: {m[1]}")
                
                cursor.execute(f"SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname = '{tenant.schema_name}';")
                tables = cursor.fetchall()
                print("\n  Tables existing:")
                for t in tables:
                    print(f"    {t[0]}")

if __name__ == "__main__":
    check_tables()
