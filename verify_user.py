from django.contrib.auth import get_user_model
from django_tenants.utils import schema_context

User = get_user_model()
try:
    with schema_context('school_a'):
        try:
            users = User.objects.all()
            print(f"TOTAL USERS IN SCHOOL_A: {users.count()}")
            for u in users:
                print(f"USER: {u.username} | ROLE: {u.role} | ACTIVE: {u.is_active} | PASS_CHECK(password123): {u.check_password('password123')}")
        except Exception as e:
            print(f"QUERY ERROR: {e}")
except Exception as e:
    print(f"CONTEXT ERROR: {e}")
