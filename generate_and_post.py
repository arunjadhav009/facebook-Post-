import os
import sys
import json
import requests
from playwright.sync_api import sync_playwright

PAGE_ID = "609269705592123"
FB_TOKEN = "EAAOiHd2BNnwBSRqv9aKYlAunjYxuVj1cl8W1Os57BlHwAJPQJhhqqZBHQ4xHQRbru8dgM3fbhzK90TrRoZBRB2CV1lV0jsYrgI01t2A7alZCJCbSdhZAcQUZCZCwlmYnOdrj585llVWO1BVZCuJ8CcWUM4ZBHPu2yANurGZCqBAFeZANlZBV13RT3xUZCANfvZCz8wkY55mAQuC67rYJh8jPiCaOz7XPE"

def generate_html_page(data):
    rows = data.get("PageData", [])
    post_date = data.get("PostDate", "आजचे भाव")
    state_name = data.get("StateName", "महाराष्ट्र")
    current_page = data.get("CurrentPage", 1)
    total_pages = data.get("TotalPages", 1)

    table_rows = ""
    for idx, r in enumerate(rows):
        is_even = (idx % 2 == 1)
        bg = "#f8fafc" if is_even else "#ffffff"
        apmc = r.get("APMC", "-")
        variety = r.get("Variety", "-")
        qty = r.get("Quantity", "0")
        lrate = r.get("Lrate", "0")
        hrate = r.get("Hrate", "0")
        modal = r.get("Modal", "0")

        table_rows += f"""
        <tr style="background: {bg}; border-bottom: 1px solid #e2e8f0;">
          <td style="text-align: left; padding: 12px 14px; font-weight: 700; font-size: 21px; color: #1e293b;">{apmc}</td>
          <td style="text-align: center; padding: 12px 8px; font-size: 19px; color: #475569; font-weight: 500;">{variety}</td>
          <td style="text-align: center; padding: 12px 8px; font-size: 20px; font-weight: 700; color: #0f172a;">{qty}</td>
          <td style="text-align: center; padding: 12px 8px; font-size: 20px; font-weight: 700; color: #dc2626;">₹{lrate}</td>
          <td style="text-align: center; padding: 12px 8px; font-size: 20px; font-weight: 700; color: #16a34a;">₹{hrate}</td>
          <td style="text-align: center; padding: 12px 8px; font-size: 22px; font-weight: 800; color: #881337; background: rgba(225, 29, 72, 0.07); border-radius: 8px;">₹{modal}</td>
        </tr>
        """

    html = f"""<!DOCTYPE html>
<html lang="mr">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;500;600;700;800&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
  body {{
    width: 1080px; height: 1080px; background: #f1f5f9;
    font-family: 'Noto Sans Devanagari', 'Arial', sans-serif;
    padding: 24px; display: flex; flex-direction: column; justify-content: space-between; overflow: hidden;
  }}
  .header-card {{
    background: linear-gradient(135deg, #881337 0%, #be123c 60%, #e11d48 100%);
    border-radius: 18px; padding: 20px 24px; color: #ffffff;
    box-shadow: 0 10px 25px -5px rgba(136, 19, 55, 0.35);
    border: 1px solid rgba(255, 255, 255, 0.15);
  }}
  .header-card h1 {{
    font-size: 34px; font-weight: 800; text-align: center; letter-spacing: 0.5px;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); margin-bottom: 12px;
  }}
  .meta-chips {{ display: flex; justify-content: space-between; align-items: center; gap: 12px; }}
  .chip {{
    background: rgba(255, 255, 255, 0.18); backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.25); padding: 6px 18px;
    border-radius: 30px; font-size: 19px; font-weight: 700;
  }}
  .table-wrapper {{
    background: #ffffff; border-radius: 18px; overflow: hidden;
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06); border: 1px solid #cbd5e1;
    margin: 12px 0; flex-grow: 1; display: flex; flex-direction: column;
  }}
  table {{ width: 100%; border-collapse: collapse; }}
  thead th {{
    background: #1e293b; color: #ffffff; font-size: 19px; font-weight: 700;
    padding: 14px 10px; text-align: center; border-bottom: 2px solid #0f172a;
  }}
  .footer-bar {{
    background: #0f172a; color: #f8fafc; border-radius: 14px;
    padding: 14px 24px; display: flex; justify-content: space-between; align-items: center;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.15);
  }}
  .footer-bar .left {{ font-size: 19px; font-weight: 700; color: #fbbf24; }}
  .footer-bar .right {{ font-size: 18px; font-weight: 600; color: #cbd5e1; }}
</style>
</head>
<body>
  <div class="header-card">
    <h1>🧅 महाराष्ट्र राज्य - आजचे कांदा बाजार भाव 🧅</h1>
    <div class="meta-chips">
      <div class="chip">तारीख: {post_date}</div>
      <div class="chip">राज्य: {state_name}</div>
      <div class="chip">पेज: {current_page} / {total_pages}</div>
    </div>
  </div>

  <div class="table-wrapper">
    <table>
      <thead>
        <tr>
          <th style="text-align: left; padding-left: 16px; width: 28%;">बाजार समिती</th>
          <th style="width: 16%;">जात/प्रकार</th>
          <th style="width: 14%;">आवक (क्विं.)</th>
          <th style="width: 14%;">कमी भाव</th>
          <th style="width: 14%;">जास्त भाव</th>
          <th style="width: 14%;">सरासरी भाव</th>
        </tr>
      </thead>
      <tbody>
        {table_rows}
      </tbody>
    </table>
  </div>

  <div class="footer-bar">
    <div class="left">⚖️ दर प्रति क्विंटल (₹)</div>
    <div class="right">दररोजच्या ताज्या बाजारभावासाठी फॉलो करा</div>
  </div>
</body>
</html>"""
    return html

def main():
    raw_pages = os.environ.get("PAGES_JSON", "").strip()
    if not raw_pages:
        print("Error: No PAGES_JSON provided.")
        sys.exit(1)

    pages_data = json.loads(raw_pages)
    print(f"Total pages received: {len(pages_data)}")

    photo_ids = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox", "--enable-font-antialiasing"]
        )
        context = browser.new_context(
            viewport={"width": 1080, "height": 1080},
            device_scale_factor=2
        )
        page = context.new_page()

        for index, item in enumerate(pages_data):
            page_info = item.get("json", item)
            html_content = generate_html_page(page_info)
            image_name = f"mandi_page_{index + 1}.png"

            print(f"Generating Ultra-HD Image {index + 1}/{len(pages_data)}: {image_name}...")
            page.set_content(html_content, wait_until="networkidle")
            page.evaluate("document.fonts.ready")
            page.screenshot(path=image_name, full_page=False)

            upload_url = f"https://graph.facebook.com/v19.0/{PAGE_ID}/photos"
            with open(image_name, "rb") as img_file:
                files = {"source": img_file}
                data = {"published": "false", "access_token": FB_TOKEN}
                res = requests.post(upload_url, files=files, data=data)
                result = res.json()

            if "id" in result:
                print(f"Page {index + 1} uploaded. Photo ID: {result['id']}")
                photo_ids.append(result["id"])
            else:
                print(f"Error uploading page {index + 1}: {result}")

        browser.close()

    if not photo_ids:
        print("No photos uploaded. Exiting.")
        sys.exit(1)

    print("Publishing final Multi-Photo Carousel Post to Facebook...")
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
