
import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

def fix_public_schema():
    print("--- Deep Cleaning Public Schema ---")
    
    # We want to keep customers_client and customers_domain!
    # These tables are not usually the source of "missing column" errors anyway.
    tables_to_drop = [
        'django_migrations',
        'django_content_type',
        'auth_permission',
        'auth_group_permissions',
        'auth_group',
        'auth_user_groups',
        'auth_user_user_permissions',
        'accounts_user_groups',
        'accounts_user_user_permissions',
        'accounts_user',
        'django_admin_log',
        'django_session',
    ]
    
    with connection.cursor() as cursor:
        for table in tables_to_drop:
            print(f"  Dropping table {table} if exists...")
            cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        
        print("  Public system tables dropped.")



if __name__ == "__main__":
    fix_public_schema()
