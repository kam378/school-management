
import os
import sys
import django

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from myapps.customers.models import Client, Domain

def create_public_tenant():
    if Client.objects.filter(schema_name='public').exists():
        print("Public tenant already exists.")
    else:
        print("Creating public tenant...")
        tenant = Client(schema_name='public', name='School Portal Public')
        tenant.save()
        print("Public tenant created.")

        domain = Domain()
        domain.domain = 'localhost' # Adjust if using a different domain
        domain.tenant = tenant
        domain.is_primary = True
        domain.save()
        print("Public domain created.")

if __name__ == "__main__":
    create_public_tenant()
