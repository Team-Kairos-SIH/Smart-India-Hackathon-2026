import os
import time
from selenium import webdriver
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By

base_dir = r"c:\Users\Gagan K S\Documents\SIH"
frontend_url = "file:///" + os.path.join(base_dir, "frontend", "index.html").replace("\\", "/")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")
options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

print("Starting Edge WebDriver...")
driver = webdriver.Edge(options=options)
driver.set_window_size(1920, 1080)

try:
    print(f"Loading {frontend_url}...")
    driver.get(frontend_url)
    
    # Wait for Leaflet map, tiles, and telemetry data to initialize
    time.sleep(5)
    
    # Photo 1: Main Web GIS Command Twin
    out1 = os.path.join(base_dir, "frontend_ui_map_twin.png")
    driver.save_screenshot(out1)
    print(f"Captured Photo 1: {out1} ({os.path.getsize(out1)} bytes)")
    
    # Interact to prepare Photo 2: Emergency Dispatch & Inspector View
    # Switch to inspector tab and select an inundated critical asset
    driver.execute_script("""
        if (typeof switchTab === 'function') {
            switchTab('inspector');
        }
        if (typeof selectAsset === 'function' && window.state && window.state.data && window.state.data.segments.length > 0) {
            // Find an inundated or critical segment, or segment index 12 (Velachery underpass)
            selectAsset(window.state.data.segments[12]);
        }
    """)
    time.sleep(2)
    
    # Photo 2: Emergency Dispatch & Infrastructure Diagnostic Inspector
    out2 = os.path.join(base_dir, "frontend_ui_emergency_dispatch.png")
    driver.save_screenshot(out2)
    print(f"Captured Photo 2: {out2} ({os.path.getsize(out2)} bytes)")

finally:
    driver.quit()
    print("WebDriver closed successfully.")
