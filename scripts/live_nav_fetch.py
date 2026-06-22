import os
import requests
import pandas as pd

# Define scheme metadata
schemes = {
    "hdfc_top100_nav.csv": 125497,
    "sbi_bluechip_nav.csv": 119551,
    "icici_bluechip_nav.csv": 120503,
    "nippon_large_cap_nav.csv": 118632,
    "axis_bluechip_nav.csv": 119092,
    "kotak_bluechip_nav.csv": 120841
}

raw_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/raw"
os.makedirs(raw_dir, exist_ok=True)

print("Starting to fetch live NAV histories...")

for filename, amfi_code in schemes.items():
    url = f"https://api.mfapi.in/mf/{amfi_code}"
    print(f"Fetching data for AMFI code {amfi_code} ({filename})...")
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        json_data = response.json()
        
        # Parse records
        records = json_data.get("data", [])
        if not records:
            print(f"Warning: No data records found for {amfi_code}.")
            continue
            
        # Create DataFrame
        df = pd.DataFrame(records)
        # Columns in response are 'date' (dd-mm-yyyy) and 'nav' (string)
        # Save as raw CSV
        dest_path = os.path.join(raw_dir, filename)
        df.to_csv(dest_path, index=False)
        print(f"Successfully saved {len(df)} rows to {dest_path}")
        
    except Exception as e:
        print(f"Error fetching data for AMFI code {amfi_code}: {e}")

print("Live NAV fetching completed.")
