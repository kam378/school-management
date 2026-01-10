
import os
import sys
import django
from django.db import connection

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from django_tenants.utils import schema_context
from myapps.customers.models import Client
from myapps.chat_system.models import ChatMessage
from django.contrib.auth import get_user_model

User = get_user_model()

def verify_chat_persistence():
    print("--- Verifying Chat Persistence & Isolation ---")
    
    tenants = Client.objects.exclude(schema_name='public')
    for tenant in tenants:
        print(f"\nChecking Tenant: {tenant.schema_name}")
        with schema_context(tenant.schema_name):
            count = ChatMessage.objects.count()
            print(f"  Message count: {count}")
            
            # Create a test message to ensure it works
            try:
                user = User.objects.all().first()
                if user:
                    ChatMessage.objects.create(
                        sender=user,
                        room_name="general",
                        content=f"Persistence test for {tenant.schema_name}"
                    )
                    new_count = ChatMessage.objects.count()
                    print(f"  [OK] Successfully created test message. New count: {new_count}")
                else:
                    print("  [SKIP] No users found in this tenant to test with.")
            except Exception as e:
                print(f"  [ERROR] Failed to save message: {e}")

if __name__ == "__main__":
    verify_chat_persistence()
