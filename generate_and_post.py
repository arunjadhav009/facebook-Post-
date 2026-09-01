import os
import pandas as pd
from playwright.sync_api import sync_playwright

SHEET_ID = "1x46h-9-vVa_QY4k3LKXDPI6F7-QScH4kIzy9q2_Kc84"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

print("1. Google Sheet से डेटा लोड हो रहा है...")
df = pd.read_csv(CSV_URL)
df.fillna("---", inplace=True)

if 'Date' in df.columns and len(df) > 0:
    latest_date = str(df.iloc[-1]['Date']).strip()
    df = df[df['Date'].astype(str).str.strip() == latest_date]
else:
    latest_date = "आजचे भाव"

records = df.to_dict('records')
records_per_page = 10
total_pages = (len(records) + records_per_page - 1) // records_per_page

os.makedirs("output_images", exist_ok=True)

def generate_html(page_records, current_page, total_p, date_str):
    rows_html = ""
    for r in page_records:
        apmc = r.get('APMC', '---')
        variety = r.get('Variety', '---')
        qty = r.get('Quantity', '0')
        lrate = r.get('Lrate', '0')
        hrate = r.get('Hrate', '0')
        modal = r.get('Modal', '0')
        rows_html += f"""
        <tr>
            <td style="text-align:left; font-weight:bold;">{apmc}</td>
            <td>{variety}</td>
            <td>{qty}</td>
            <td style="color:#e53e3e; font-weight:bold;">₹{lrate}</td>
            <td style="color:#38a169; font-weight:bold;">₹{hrate}</td>
            <td style="color:#b31217; font-weight:800; font-size:22px;">₹{modal}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Noto Sans Devanagari', sans-serif; }}
  body {{
    width: 1080px;
    height: 1080px;
    background: #f4f6f9;
    padding: 35px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .header {{
    background: linear-gradient(135deg, #b31217, #e52d27);
    color: white;
    padding: 24px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
  }}
  .header h1 {{ font-size: 38px; font-weight: 800; margin-bottom: 8px; }}
  .header .sub {{ font-size: 20px; display: flex; justify-content: space-between; padding: 0 15px; }}
  table {{
    width: 100%;
    border-collapse: collapse;
    background: white;
    border-radius: 16px;
    overflow: hidden;
    box-shadow: 0 6px 14px rgba(0,0,0,0.08);
  }}
  th {{
    background: #1e293b;
    color: white;
    font-size: 20px;
    padding: 14px 10px;
    text-align: center;
  }}
  td {{
    font-size: 19px;
    padding: 12px 8px;
    text-align: center;
    border-bottom: 1px solid #edf2f7;
    color: #334155;
  }}
  tr:nth-child(even) {{ background-color: #f8fafc; }}
  .footer {{
    background: #1e293b;
    color: white;
    padding: 16px 24px;
    border-radius: 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 20px;
  }}
</style>
</head>
<body>
  <div class="header">
    <h1>🧅 महाराष्ट्र कांदा बाजार भाव 🧅</h1>
    <div class="sub">
      <span>तारीख: {date_str}</span>
      <span>पान: {current_page} / {total_p}</span>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th style="text-align:left;">बाजार समिती</th>
        <th>जात</th>
        <th>आवक (क्विं.)</th>
        <th>कमी भाव</th>
        <th>जास्त भाव</th>
        <th>सरासरी भाव</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <div class="footer">
    <span>दर प्रति क्विंटल (₹)</span>
    <span>🌾 दररोजच्या ताज्या बाजारभावासाठी फॉलो करा</span>
  </div>
</body>
</html>"""

print("2. 1:1 HD Images Generate हो रही हैं...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1080, "height": 1080})

    for i in range(total_pages):
        chunk = records[i*records_per_page : (i+1)*records_per_page]
        html_code = generate_html(chunk, i + 1, total_pages, latest_date)
        page.set_content(html_code)
        img_path = f"output_images/page_{i+1}.png"
        page.screenshot(path=img_path)
        print(f"तैयार हो गई: {img_path}")

    browser.close()

print("सफलतापूर्वक सभी इमेज बन गईं!")
