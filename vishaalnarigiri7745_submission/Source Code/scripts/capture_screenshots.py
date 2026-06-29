import os
import time
from playwright.sync_api import sync_playwright
from PIL import Image

def capture():
    charts_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/reports/charts"
    reports_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/reports"
    os.makedirs(charts_dir, exist_ok=True)

    url = "http://localhost:8502"
    screenshots = []

    with sync_playwright() as p:
        print("Launching Chromium browser via Playwright...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_viewport_size({"width": 1920, "height": 1080})
        
        # 1. Page 1: Industry Overview
        print("Navigating to Streamlit App (Page 1: Industry Overview)...")
        page.goto(url)
        page.wait_for_load_state("networkidle")
        time.sleep(6)  # Wait for charts and animations
        p1_path = os.path.join(charts_dir, "Page1_Industry_Overview.png")
        page.screenshot(path=p1_path, full_page=True)
        screenshots.append(p1_path)
        print("Page 1 screenshot captured.")

        # 2. Page 2: Fund Performance
        print("Clicking Navigation to Page 2: Fund Performance...")
        page.locator("text=Fund Performance").first.click()
        time.sleep(6)
        p2_path = os.path.join(charts_dir, "Page2_Fund_Performance.png")
        page.screenshot(path=p2_path, full_page=True)
        screenshots.append(p2_path)
        print("Page 2 screenshot captured.")

        # 3. Page 3: Investor Analytics
        print("Clicking Navigation to Page 3: Investor Analytics...")
        page.locator("text=Investor Analytics").first.click()
        time.sleep(6)
        p3_path = os.path.join(charts_dir, "Page3_Investor_Analytics.png")
        page.screenshot(path=p3_path, full_page=True)
        screenshots.append(p3_path)
        print("Page 3 screenshot captured.")

        # 4. Page 4: SIP & Market Trends
        print("Clicking Navigation to Page 4: SIP & Market Trends...")
        page.locator("text=SIP & Market Trends").first.click()
        time.sleep(6)
        p4_path = os.path.join(charts_dir, "Page4_SIP_Market_Trends.png")
        page.screenshot(path=p4_path, full_page=True)
        screenshots.append(p4_path)
        print("Page 4 screenshot captured.")

        browser.close()

    # Compile screenshots into PDF
    print("Compiling screenshots into PDF...")
    pdf_path = os.path.join(reports_dir, "Dashboard.pdf")
    img_list = [Image.open(img).convert("RGB") for img in screenshots]
    img_list[0].save(pdf_path, save_all=True, append_images=img_list[1:])
    print(f"Dashboard PDF compiled successfully at {pdf_path}")

if __name__ == "__main__":
    capture()
