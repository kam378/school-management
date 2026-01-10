
import os
import sys
import re
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from django.utils.text import slugify
from myapps.customers.models import Client, Domain

def get_input(prompt, default=None):
    if default:
        user_input = input(f"{prompt} [{default}]: ")
        return user_input.strip() or default
    else:
        while True:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input

def create_tenant():
    print("=== Create New Tenant ===")
    
    # 1. Tenant Name
    name = get_input("Enter School Name")
    
    # 2. Schema Name
    default_schema = slugify(name).replace('-', '_')
    schema_name = get_input("Enter Schema Name (db schema)", default=default_schema)
    
    # Validate schema name (must be valid postgres identifier)
    if not re.match(r'^[a-z0-9_]+$', schema_name):
        print("Error: Schema name can only contain lowercase letters, numbers, and underscores.")
        return

    if Client.objects.filter(schema_name=schema_name).exists():
        print(f"Error: Tenant with schema '{schema_name}' already exists.")
        return

    # 3. Domain
    default_domain = f"{slugify(name)}.localhost"
    domain_url = get_input("Enter Domain", default=default_domain)

    if Domain.objects.filter(domain=domain_url).exists():
        print(f"Error: Domain '{domain_url}' already exists.")
        return

    try:
        print(f"\nCreating tenant '{name}' with schema '{schema_name}'...")
        tenant = Client(schema_name=schema_name, name=name)
        tenant.save()
        print("Tenant created successfully.")

        print(f"Creating domain '{domain_url}'...")
        domain = Domain()
        domain.domain = domain_url
        domain.tenant = tenant
        domain.is_primary = True
        domain.save()
        print("Domain created successfully.")
        
        print("\nDone! You can now access the tenant at:")
        print(f"http://{domain_url}:8000")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_tenant()
