
import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from myapps.customers.models import Client, Domain

def create_tenant(name, schema_name, domain_name):
    if Client.objects.filter(schema_name=schema_name).exists():
        print(f"Tenant '{name}' ({schema_name}) already exists.")
        return Client.objects.get(schema_name=schema_name)
    
    print(f"Creating tenant '{name}' with schema '{schema_name}'...")
    tenant = Client(schema_name=schema_name, name=name)
    tenant.save()
    
    domain = Domain()
    domain.domain = domain_name
    domain.tenant = tenant
    domain.is_primary = True
    domain.save()
    print(f"Tenant and domain '{domain_name}' created.")
    return tenant

if __name__ == "__main__":
    # 1. Public Tenant
    create_tenant('School Portal Public', 'public', 'localhost')
    
    # 2. School A
    create_tenant('School A', 'school_a', 'school-a.localhost')
    
    # 3. School B
    create_tenant('School B', 'school_b', 'school-b.localhost')
    
    # 4. Demo School Two
    create_tenant('Demo School Two', 'demo_school_two', 'demo-school-two.localhost')
    
    print("\nAll tenants initialized successfully.")
