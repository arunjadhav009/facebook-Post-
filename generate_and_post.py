import os
import sys
import requests
from playwright.sync_api import sync_playwright

def main():
    html_content = os.environ.get("INPUT_HTML", "").strip()
    webhook_url = os.environ.get("N8N_WEBHOOK_URL", "").strip()
    output_image = "mandi_bhav_page.png"

    if not html_content:
        print("Error: No INPUT_HTML content provided.")
        sys.exit(1)

    print("Generating 1080x1080 HD image with Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(html_content, wait_until="networkidle")
        page.screenshot(path=output_image, full_page=False)
        browser.close()

    print(f"Image created successfully: {output_image}")

    if webhook_url and os.path.exists(output_image):
        print(f"Sending raw binary image to n8n Webhook: {webhook_url}")
        with open(output_image, "rb") as img_file:
            image_bytes = img_file.read()
            
        headers = {"Content-Type": "image/png"}
        response = requests.post(webhook_url, data=image_bytes, headers=headers)
        print(f"n8n Response Status Code: {response.status_code}")
        print(f"n8n Response: {response.text}")
    else:
        print("Error: N8N_WEBHOOK_URL missing or image file not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
