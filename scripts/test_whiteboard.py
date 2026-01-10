import os
import sys
import requests
from dotenv import load_dotenv

# Load env variables directly to avoid django setup overhead for this simple test
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'))

AGORA_REST_ID = os.environ.get("AGORA_REST_ID")
AGORA_REST_CERTIFICATE = os.environ.get("AGORA_REST_CERTIFICATE")
BASE_URL = "https://api.netless.link/v5"

print(f"Testing with REST_ID: {AGORA_REST_ID[:5]}... (Redacted)")

def test_token_generation():
    print("\n[1] Testing Token Generation...")
    url = f"{BASE_URL}/tokens/rooms/test-uuid"
    headers = {
        "content-type": "application/json",
        "token": AGORA_REST_CERTIFICATE,
        "region": "cn-hz"
    }
    data = {"lifespan": 1000, "role": "admin"}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()
        print("✅ Token Generation API Reached!")
    except Exception as e:
        print(f"❌ Token Failed: {e}")

def test_room_creation():
    print("\n[2] Testing Room Creation...")
    url = f"{BASE_URL}/rooms"
    headers = {
        "content-type": "application/json",
        "token": AGORA_REST_CERTIFICATE,
        "region": "cn-hz"
    }
    data = {"isRecord": False, "limit": 0}
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 201 or response.status_code == 200:
             print(f"Response: {response.json()}")
             print("✅ Room Creation Successful!")
        else:
             print(f"❌ Failed: {response.text}")
    except Exception as e:
        print(f"❌ Room Creation Failed: {e}")

if __name__ == "__main__":
    test_token_generation()
    test_room_creation()
