import os
import sys
import json
import requests
from playwright.sync_api import sync_playwright

PAGE_ID = "609269705592123"
FB_TOKEN = "EAAOiHd2BNnwBSRqv9aKYlAunjYxuVj1cl8W1Os57BlHwAJPQJhhqqZBHQ4xHQRbru8dgM3fbhzK90TrRoZBRB2CV1lV0jsYrgI01t2A7alZCJCbSdhZAcQUZCZCwlmYnOdrj585llVWO1BVZCuJ8CcWUM4ZBHPu2yANurGZCqBAFeZANlZBV13RT3xUZCANfvZCz8wkY55mAQuC67rYJh8jPiCaOz7XPE"

def main():
    raw_html_list = os.environ.get("INPUT_HTML_LIST", "").strip()

    if not raw_html_list:
        print("Error: No INPUT_HTML_LIST provided.")
        sys.exit(1)

    try:
        html_pages = json.loads(raw_html_list)
    except Exception as e:
        # सिंगल HTML असल्यास लिस्ट बनवा
        html_pages = [raw_html_list]

    print(f"Total pages to generate: {len(html_pages)}")

    photo_ids = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1080, "height": 1080})

        for index, html_content in enumerate(html_pages):
            image_name = f"mandi_page_{index + 1}.png"
            print(f"Generating Image {index + 1}/{len(html_pages)}: {image_name}...")
            
            page.set_content(html_content, wait_until="networkidle")
            page.screenshot(path=image_name, full_page=False)

            # Facebook वर Unpublished फोटो अपलोड करणे
            upload_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
            with open(image_name, "rb") as img_file:
                files = {"source": img_file}
                data = {
                    "published": "false",
                    "access_token": FB_TOKEN
                }
                res = requests.post(upload_url, files=files, data=data)
                result = res.json()

            if "id" in result:
                print(f"Uploaded page {index + 1} successfully. ID: {result['id']}")
                photo_ids.append(result["id"])
            else:
                print(f"Error uploading page {index + 1}: {result}")

        browser.close()

    if not photo_ids:
        print("No photos uploaded. Exiting.")
        sys.exit(1)

    # सर्व फोटो एकत्र करून १ सिंगल अल्बम पोस्ट तयार करणे
    print("Publishing final Multi-Photo Album Post to Facebook...")
    feed_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/feed"
    
    attached_media = [{"media_fbid": pid} for pid in photo_ids]
    
    post_payload = {
        "message": "महाराष्ट्र राज्य कांदा बाजारभाव\n\nदररोजच्या ताज्या बाजारभावासाठी पेजला नक्की फॉलो करा!\n#कांदा #बाजारभाव #महाराष्ट्र #OnionRates #Maharashtra",
        "attached_media": json.dumps(attached_media),
        "access_token": FB_TOKEN
    }

    resp = requests.post(feed_url, data=post_payload)
    print("Facebook Post Response:", resp.text)

if __name__ == "__main__":
    main()
