import os
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options

base_dir = r"c:\Users\Gagan K S\Documents\SIH"
frontend_url = "file:///" + os.path.join(base_dir, "frontend", "index.html").replace("\\", "/")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print("Launching Edge Headless WebDriver...")
driver = webdriver.Edge(options=options)
driver.set_window_size(1920, 1080)

try:
    print(f"Loading {frontend_url}...")
    driver.get(frontend_url)
    time.sleep(3)

    # Switch to National GIGW Light Skin Mode
    print("Switching to National GIGW Light Skin Mode...")
    driver.execute_script("setSkin('gigw');")
    time.sleep(4)

    # Capture high-res screenshot
    out_path = os.path.join(base_dir, "frontend_ui_gigw_light.png")
    driver.save_screenshot(out_path)
    print(f"[+] Successfully captured: {out_path} ({os.path.getsize(out_path)} bytes)")

finally:
    driver.quit()
    print("Edge driver closed.")
