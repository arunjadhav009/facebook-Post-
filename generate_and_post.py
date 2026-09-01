import os
import json
import requests
from playwright.sync_api import sync_playwright

input_data_str = os.environ.get("INPUT_DATA", "").strip()
N8N_WEBHOOK_URL = os.environ.get("N8N_WEBHOOK_URL", "").strip()

os.makedirs("output_images", exist_ok=True)

# n8n कडून आलेले सर्व पेजेस
pages = json.loads(input_data_str) if input_data_str else []

if not pages:
    print("No pages received!")
    exit(0)

generated_files = []

print(f"Total Pages to generate: {len(pages)}")

with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
    page = browser.new_page(viewport={"width": 1080, "height": 1080})

    # क्रमाने एकामागोमाग एक इमेज बनवणे (1, 2, 3...)
    for idx, p_data in enumerate(pages):
        html_code = p_data.get("htmlCode", "")
        img_path = f"output_images/page_{idx + 1}.png"
        
        page.set_content(html_code)
        page.screenshot(path=img_path)
        print(f"✅ Generated Page {idx + 1}: {img_path}")
        generated_files.append(img_path)

    browser.close()

# सर्व इमेजेस एकाच वेळी n8n Webhook ला पाठवणे
if N8N_WEBHOOK_URL and generated_files:
    print(f"Sending all {len(generated_files)} images to n8n Webhook...")
    
    files_to_send = []
    opened_files = []
    
    for i, f_path in enumerate(generated_files):
        f = open(f_path, 'rb')
        opened_files.append(f)
        files_to_send.append(('files', (f'page_{i+1}.png', f, 'image/png')))
    
    # n8n ला पोस्ट करणे
    res = requests.post(N8N_WEBHOOK_URL, files=files_to_send)
    print("n8n Response Status:", res.status_code)
    
    # फाइल्स बंद करणे
    for f in opened_files:
        f.close()

print("All Done Successfully!")
