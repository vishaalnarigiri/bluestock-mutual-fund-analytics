import pandas as pd

master_path = "/Users/vaishnavnarigiri/Desktop/bluestock/data/raw/01_fund_master.csv"
nav_path = "/Users/vaishnavnarigiri/Desktop/bluestock/data/raw/02_nav_history.csv"

# Load datasets
df_master = pd.read_csv(master_path)
df_nav = pd.read_csv(nav_path)

# Step 4: Understand Fund Master
fund_houses = df_master["fund_house"].unique()
categories = df_master["category"].unique()
sub_categories = df_master["sub_category"].unique()
risk_categories = df_master["risk_category"].unique()
amfi_codes = df_master["amfi_code"].unique()

print("=== Step 4: Fund Master Analysis ===")
print(f"Total Fund Houses: {len(fund_houses)}")
print(f"Fund Houses: {list(fund_houses)}")
print(f"Total Categories: {len(categories)}")
print(f"Categories: {list(categories)}")
print(f"Sub-categories: {list(sub_categories)}")
print(f"Total Risk Categories (Grades): {len(risk_categories)}")
print(f"Risk Categories: {list(risk_categories)}")
print(f"Total AMFI Codes in Master: {len(amfi_codes)}")
print()

# Step 5: Validate Data
master_codes = set(df_master["amfi_code"])
nav_codes = set(df_nav["amfi_code"])

missing_codes = master_codes - nav_codes

print("=== Step 5: Data Validation ===")
print(f"Checking if all {len(master_codes)} master AMFI codes exist in NAV history...")
if len(missing_codes) == 0:
    print("All 40 AMFI codes found.")
    print("No missing schemes.")
else:
    print(f"Warning: {len(missing_codes)} AMFI codes from master are missing in NAV history!")
    print(f"Missing codes: {missing_codes}")
