
import os
import sys
import django
from django.contrib.auth import get_user_model

# Add project root to path
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

def create_public_admin():
    from django_tenants.utils import schema_context
    User = get_user_model()
    with schema_context('public'):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@localhost', 'admin_pass')
            print("Public superuser created: admin / admin_pass")
        else:
            print("Public superuser 'admin' already exists.")

if __name__ == "__main__":
    create_public_admin()
