import os
import django
import sys

# Setup Django Environment manually
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

User = get_user_model()
try:
    print("--- START PUBLIC VERIFICATION ---")
    with schema_context('public'):
        users = User.objects.all()
        print(f"TOTAL USERS IN PUBLIC: {users.count()}")
        for u in users:
            print(f"USER: {u.username} | ROLE: '{u.role}'")
    print("--- END PUBLIC VERIFICATION ---")
except Exception as e:
    print(f"ERROR: {e}")
