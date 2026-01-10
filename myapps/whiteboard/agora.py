import os
import requests

AGORA_REST_ID = os.getenv("AGORA_REST_ID")
AGORA_REST_CERTIFICATE = os.getenv("AGORA_REST_CERTIFICATE")

BASE_URL = "https://api.netless.link/v5"

# Validate env variables
if not AGORA_REST_ID or not AGORA_REST_CERTIFICATE:
    raise RuntimeError("Missing Agora REST credentials! Check your .env file.")

def generate_room_token(room_uuid: str, is_teacher: bool):
    role = "admin" if is_teacher else "reader"
    url = f"{BASE_URL}/tokens/rooms/{room_uuid}"

    headers = {
        "content-type": "application/json",
        "token": AGORA_REST_CERTIFICATE,
        "region": "sg"  # Switched from cn-hz for better connectivity
    }

    data = {
        "lifespan": 3600000,  # 1 hour
        "role": role
    }

    try:
        print(f"DEBUG Netless: Creating Token for UUID={room_uuid} in Region=sg")
        response = requests.post(url, json=data, headers=headers, timeout=5)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"DEBUG Netless Error: {e.response.text if hasattr(e, 'response') else e}")
        raise RuntimeError(f"Failed to generate Agora token: {e}")

    result = response.json()
    if isinstance(result, str):
        return result
    return result.get("token")

def create_room(name: str = "Whiteboard Room", limit: int = 0):
    """
    Creates a room on Agora/Netless server and returns the Room UUID.
    API: POST https://api.netless.link/v5/rooms
    """
    url = f"{BASE_URL}/rooms"
    
    headers = {
        "content-type": "application/json",
        "token": AGORA_REST_CERTIFICATE,
        "region": "sg" # Switched from cn-hz for better global connectivity
    }
    
    data = {
        "isRecord": False,
        "limit": limit
    }
    
    try:
        print(f"DEBUG Netless: Creating NEW Room in Region=sg")
        response = requests.post(url, json=data, headers=headers, timeout=10)
        response.raise_for_status()
        
        result = response.json()
        uuid = result.get("uuid")
        print(f"DEBUG Netless: Room Created Successfully! UUID={uuid}")
        return uuid
        
    except requests.RequestException as e:
        print(f"DEBUG Netless Error: {e.response.text if hasattr(e, 'response') else e}")
        raise RuntimeError(f"Failed to create Agora room: {e}")
