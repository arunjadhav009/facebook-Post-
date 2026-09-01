import os
from playwright.sync_api import sync_playwright

# n8n se bheja gaya HTML lena
input_html = os.environ.get("INPUT_HTML", "").strip()

os.makedirs("output_images", exist_ok=True)

if not input_html:
    print("Warning: Koi HTML nahi mila, test HTML use kar rahe hain.")
    input_html = "<html><body style='display:flex;justify-content:center;align-items:center;height:100vh;'><h1>Mandi Bhav Test</h1></body></html>"

print("1:1 HD Image Generate ho rahi hai...")
with sync_playwright() as p:
    browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox"])
    page = browser.new_page(viewport={"width": 1080, "height": 1080})
    page.set_content(input_html)
    img_path = "output_images/page_1.png"
    page.screenshot(path=img_path)
    print(f"Image successfully ban gayi: {img_path}")
    browser.close()

print("Process Complete!")
