import os
import sys
import json
import requests
from playwright.sync_api import sync_playwright

PAGE_ID = "609269705592123"
FB_TOKEN = "EAAOiHd2BNnwBSRqv9aKYlAunjYxuVj1cl8W1Os57BlHwAJPQJhhqqZBHQ4xHQRbru8dgM3fbhzK90TrRoZBRB2CV1lV0jsYrgI01t2A7alZCJCbSdhZAcQUZCZCwlmYnOdrj585llVWO1BVZCuJ8CcWUM4ZBHPu2yANurGZCqBAFeZANlZBV13RT3xUZCANfvZCz8wkY55mAQuC67rYJh8jPiCaOz7XPE"

def main():
    html_content = os.environ.get("INPUT_HTML", "").strip()

    if not html_content:
        print("Error: No INPUT_HTML content provided.")
        sys.exit(1)

    output_image = "mandi_bhav_page.png"
    print("Generating 1080x1080 HD image with Playwright...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})
        page.set_content(html_content, wait_until="networkidle")
        page.screenshot(path=output_image, full_page=False)
        browser.close()

    print(f"Image created: {output_image}")

    # १. फोटो Unpublished म्हणून अपलोड करणे
    upload_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
    with open(output_image, "rb") as img_file:
        files = {"source": img_file}
        data = {
            "published": "false",
            "access_token": FB_TOKEN
        }
        res = requests.post(upload_url, files=files, data=data)
        photo_data = res.json()

    if "id" not in photo_data:
        print(f"Error uploading photo to FB: {photo_data}")
        sys.exit(1)

    photo_id = photo_data["id"]
    print(f"Photo uploaded unpublished successfully. Photo ID: {photo_id}")

    # २. फोटो आयडी n8n कडे गोळा करण्यासाठी पाठवणे
    webhook_url = os.environ.get("N8N_WEBHOOK_URL", "").strip()
    if webhook_url:
        resp = requests.post(webhook_url, json={"photo_id": photo_id})
        print(f"Sent Photo ID to n8n. Status: {resp.status_code}")

if __name__ == "__main__":
    main()
