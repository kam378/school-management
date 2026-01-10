import os
import requests

# Ensure directory exists
target_dir = os.path.join("myapps", "whiteboard", "static", "whiteboard", "js")
os.makedirs(target_dir, exist_ok=True)

# We need 3 files for the full setup
files = {
    "fastboard.js": "https://esm.sh/@netless/fastboard@1.1.0/es2022/fastboard.bundle.mjs",
    "white-web-sdk.js": "https://esm.sh/white-web-sdk@2.16.45?target=es2022",
    "window-manager.js": "https://esm.sh/@netless/window-manager@1.0.19?target=es2022"
}

for filename, url in files.items():
    target_file = os.path.join(target_dir, filename)
    print(f"Downloading {filename} from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Save to file. bundling might be binary or text, write generic binary is safer
        with open(target_file, "wb") as f:
            f.write(response.content)
        
        print(f"SUCCESS: Saved to {target_file}")
        print(f"Size: {len(response.content)} bytes")

    except Exception as e:
        print(f"FAILURE: {e}")
