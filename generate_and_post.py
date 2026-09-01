import os
import requests

N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "").strip()
img_path = "output.png"  # किंवा तुमच्या जनरेट झालेल्या इमेजचे नाव

if N8N_WEBHOOK_URL and os.path.exists(img_path):
    print(f"Sending image to: {N8N_WEBHOOK_URL}")
    
    # n8n च्या बायनरी 'data' प्रॉपर्टीसाठी फाईल पाठवणे
    with open(img_path, "rb") as image_file:
        files = {
            "data": (os.path.basename(img_path), image_file, "image/png")
        }
        response = requests.post(N8N_WEBHOOK_URL, files=files)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
