import os
import django
import sys

# Setup Django Environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_portal.settings')
django.setup()

from myapps.whiteboard.agora import generate_room_token

room_uuid = "test-room-uuid-123"
print(f"Testing Token Generation for Room: {room_uuid}")

try:
    token = generate_room_token(room_uuid, is_teacher=True)
    if token:
        print("SUCCESS! Token generated:")
        print(token[:50] + "...") # Print first 50 chars for verification
    else:
        print("FAILURE: Token was empty.")
except Exception as e:
    print(f"FAILURE: Exception occurred: {e}")
