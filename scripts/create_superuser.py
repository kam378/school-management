
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

def get_input(prompt, hidden=False):
    if hidden:
        import getpass
        return getpass.getpass(prompt)
    return input(f"{prompt}: ").strip()

def create_superuser():
    print("=== Create Tenant Superuser ===")
    
    # 1. List Tenants
    tenants = Client.objects.all().order_by('schema_name')
    if not tenants.exists():
        print("No tenants found! Please create a tenant first.")
        return

    print("\nAvailable Tenants:")
    for idx, tenant in enumerate(tenants):
        print(f"[{idx + 1}] {tenant.name} ({tenant.schema_name})")

    # 2. Select Tenant
    while True:
        try:
            choice = int(get_input("\nSelect a tenant by number"))
            if 1 <= choice <= len(tenants):
                selected_tenant = tenants[choice - 1]
                break
            print("Invalid selection.")
        except ValueError:
            print("Please enter a number.")

    print(f"\nCreating superuser for: {selected_tenant.name} ({selected_tenant.schema_name})")

    # 3. Get Credentials
    username = get_input("Username")
    email = get_input("Email")
    password = get_input("Password", hidden=True)

    # 4. Create User in Tenant Context
    try:
        with schema_context(selected_tenant.schema_name):
            User = get_user_model()
            if User.objects.filter(username=username).exists():
                print(f"Error: User '{username}' already exists in this tenant.")
                return

            User.objects.create_superuser(username=username, email=email, password=password)
            print(f"\nSuccess! Superuser '{username}' created for '{selected_tenant.name}'.")
            
            # Show login URL
            domain = selected_tenant.domains.first()
            if domain:
                port = ":8000"  # Assuming dev server port
                print(f"Login here: http://{domain.domain}{port}/admin")
            
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    create_superuser()
