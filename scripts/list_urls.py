import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from myapps.customers.models import Domain

def list_tenant_urls():
    print("-" * 60)
    print(f"{'TENANT':<20} | {'FULL URL':<35}")
    print("-" * 60)
    
    domains = Domain.objects.all()
    for d in domains:
        url = f"http://{d.domain}:8000"
        print(f"{d.tenant.schema_name:<20} | {url:<35}")
    
    print("-" * 60)

if __name__ == "__main__":
    list_tenant_urls()
