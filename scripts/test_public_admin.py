
import os
import sys
import django
from django.urls import resolve, reverse
from django.conf import settings

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

def test_public_admin():
    print("--- Testing Public Admin Access ---")
    try:
        from django.urls import set_urlconf
        set_urlconf('school_portal.public_urls')
        
        from django.contrib import admin
        print(f"Registered models in public admin: {list(admin.site._registry.keys())}")
        
        # Check if Client and Domain are there
        from myapps.customers.models import Client, Domain
        if Client in admin.site._registry:
            print("[OK] Client model is registered.")
        else:
            print("[ERROR] Client model is NOT registered in public admin.")
            
        # Try to reverse a model admin URL
        url = reverse('admin:customers_client_changelist')
        print(f"Client changelist URL: {url}")
        
    except Exception as e:
        print(f"[ERROR] Public Admin Issue: {e}")

if __name__ == "__main__":
    test_public_admin()
