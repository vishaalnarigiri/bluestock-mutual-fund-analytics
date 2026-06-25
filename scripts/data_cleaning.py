import os
import pandas as pd
import numpy as np

raw_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/raw"
processed_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/processed"
os.makedirs(processed_dir, exist_ok=True)

# 1. Clean 01_fund_master.csv
print("Cleaning 01_fund_master.csv...")
df_master = pd.read_csv(os.path.join(raw_dir, "01_fund_master.csv"))
df_master["launch_date"] = pd.to_datetime(df_master["launch_date"]).dt.strftime('%Y-%m-%d')
df_master["expense_ratio_pct"] = pd.to_numeric(df_master["expense_ratio_pct"], errors='coerce')
df_master["exit_load_pct"] = pd.to_numeric(df_master["exit_load_pct"], errors='coerce').fillna(0.0)
df_master["min_sip_amount"] = pd.to_numeric(df_master["min_sip_amount"], errors='coerce').astype(int)
df_master["min_lumpsum_amount"] = pd.to_numeric(df_master["min_lumpsum_amount"], errors='coerce').astype(int)
df_master.to_csv(os.path.join(processed_dir, "01_fund_master.csv"), index=False)

# 2. Clean 02_nav_history.csv
print("Cleaning 02_nav_history.csv...")
df_nav = pd.read_csv(os.path.join(raw_dir, "02_nav_history.csv"))
df_nav["date"] = pd.to_datetime(df_nav["date"])
df_nav["nav"] = pd.to_numeric(df_nav["nav"], errors='coerce')

# Validate NAV > 0: Remove any row where NAV is <= 0 or missing
invalid_nav = (df_nav["nav"] <= 0) | df_nav["nav"].isnull()
if invalid_nav.any():
    print(f"Removing {invalid_nav.sum()} rows with invalid NAV (<= 0 or null).")
    df_nav = df_nav[~invalid_nav]

# Forward fill missing NAV values on weekends/holidays for each scheme
cleaned_nav_groups = []
for amfi, group in df_nav.groupby("amfi_code"):
    group = group.drop_duplicates(subset=["date"]).set_index("date")
    # Generate full date range
    all_dates = pd.date_range(start=group.index.min(), end=group.index.max(), freq="D")
    group = group.reindex(all_dates)
    group["amfi_code"] = amfi
    group["nav"] = group["nav"].ffill() # Forward fill
    group = group.reset_index().rename(columns={"index": "date"})
    cleaned_nav_groups.append(group)

df_nav_clean = pd.concat(cleaned_nav_groups, ignore_index=True)
df_nav_clean["date"] = df_nav_clean["date"].dt.strftime('%Y-%m-%d')
df_nav_clean.sort_values(by=["amfi_code", "date"], inplace=True)

# Final validation check
final_invalid_nav = df_nav_clean["nav"] <= 0
if final_invalid_nav.any():
    print(f"Warning: Found {final_invalid_nav.sum()} rows in final data where NAV <= 0. Removing.")
    df_nav_clean = df_nav_clean[~final_invalid_nav]

df_nav_clean.to_csv(os.path.join(processed_dir, "02_nav_history.csv"), index=False)


# 3. Clean 03_aum_by_fund_house.csv
print("Cleaning 03_aum_by_fund_house.csv...")
df_aum = pd.read_csv(os.path.join(raw_dir, "03_aum_by_fund_house.csv"))
df_aum["date"] = pd.to_datetime(df_aum["date"]).dt.strftime('%Y-%m-%d')
df_aum["aum_lakh_crore"] = pd.to_numeric(df_aum["aum_lakh_crore"], errors='coerce')
df_aum["aum_crore"] = pd.to_numeric(df_aum["aum_crore"], errors='coerce').astype(int)
df_aum["num_schemes"] = pd.to_numeric(df_aum["num_schemes"], errors='coerce').astype(int)
df_aum.to_csv(os.path.join(processed_dir, "03_aum_by_fund_house.csv"), index=False)

# 4. Clean 04_monthly_sip_inflows.csv
print("Cleaning 04_monthly_sip_inflows.csv...")
df_sip = pd.read_csv(os.path.join(raw_dir, "04_monthly_sip_inflows.csv"))
df_sip["sip_inflow_crore"] = pd.to_numeric(df_sip["sip_inflow_crore"], errors='coerce').astype(int)
df_sip["active_sip_accounts_crore"] = pd.to_numeric(df_sip["active_sip_accounts_crore"], errors='coerce')
df_sip["new_sip_accounts_lakh"] = pd.to_numeric(df_sip["new_sip_accounts_lakh"], errors='coerce')
df_sip["sip_aum_lakh_crore"] = pd.to_numeric(df_sip["sip_aum_lakh_crore"], errors='coerce')
df_sip["yoy_growth_pct"] = pd.to_numeric(df_sip["yoy_growth_pct"], errors='coerce').fillna(0.0)
df_sip.to_csv(os.path.join(processed_dir, "04_monthly_sip_inflows.csv"), index=False)

# 5. Clean 05_category_inflows.csv
print("Cleaning 05_category_inflows.csv...")
df_cat = pd.read_csv(os.path.join(raw_dir, "05_category_inflows.csv"))
df_cat["net_inflow_crore"] = pd.to_numeric(df_cat["net_inflow_crore"], errors='coerce')
df_cat.to_csv(os.path.join(processed_dir, "05_category_inflows.csv"), index=False)

# 6. Clean 06_industry_folio_count.csv
print("Cleaning 06_industry_folio_count.csv...")
df_folio = pd.read_csv(os.path.join(raw_dir, "06_industry_folio_count.csv"))
for col in ["total_folios_crore", "equity_folios_crore", "debt_folios_crore", "hybrid_folios_crore", "others_folios_crore"]:
    df_folio[col] = pd.to_numeric(df_folio[col], errors='coerce')
df_folio.to_csv(os.path.join(processed_dir, "06_industry_folio_count.csv"), index=False)

# 7. Clean 07_scheme_performance.csv
print("Cleaning 07_scheme_performance.csv...")
df_perf = pd.read_csv(os.path.join(raw_dir, "07_scheme_performance.csv"))
# Validate numeric fields
numeric_cols = [
    "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "benchmark_3yr_pct",
    "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct",
    "max_drawdown_pct", "aum_crore", "expense_ratio_pct"
]
for col in numeric_cols:
    df_perf[col] = pd.to_numeric(df_perf[col], errors='coerce')

# Flag negative Sharpe ratios
df_perf["negative_sharpe_flag"] = (df_perf["sharpe_ratio"] < 0).astype(int)

# Validate expense ratio ranges (usually 0.1% to 2.5%)
df_perf["expense_ratio_valid"] = df_perf["expense_ratio_pct"].between(0.1, 2.5).astype(int)
df_perf.to_csv(os.path.join(processed_dir, "07_scheme_performance.csv"), index=False)

# 8. Clean 08_investor_transactions.csv
print("Cleaning 08_investor_transactions.csv...")
df_tx = pd.read_csv(os.path.join(raw_dir, "08_investor_transactions.csv"))
df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"]).dt.strftime('%Y-%m-%d')
tx_map = {
    "SIP": "SIP", "Sip": "SIP", "sip": "SIP",
    "Lumpsum": "Lumpsum", "LUMP-SUM": "Lumpsum", "lumpsum": "Lumpsum",
    "Redemption": "Redemption", "redemption": "Redemption", "REDEMPTION": "Redemption"
}
df_tx["transaction_type"] = df_tx["transaction_type"].map(tx_map).fillna(df_tx["transaction_type"])

# Remove invalid entries (amount_inr <= 0)
invalid_tx = df_tx["amount_inr"] <= 0
if invalid_tx.any():
    print(f"Removing {invalid_tx.sum()} transactions with invalid amounts (<= 0).")
    df_tx = df_tx[~invalid_tx]

# Standardize KYC status values to 'Verified' and 'Pending'
kyc_map = {
    "Verified": "Verified", "VERIFIED": "Verified", "verified": "Verified",
    "Pending": "Pending", "PENDING": "Pending", "pending": "Pending"
}
df_tx["kyc_status"] = df_tx["kyc_status"].map(kyc_map).fillna("Pending")

df_tx.to_csv(os.path.join(processed_dir, "08_investor_transactions.csv"), index=False)

# 9. Clean 09_portfolio_holdings.csv
print("Cleaning 09_portfolio_holdings.csv...")
df_port = pd.read_csv(os.path.join(raw_dir, "09_portfolio_holdings.csv"))
df_port["weight_pct"] = pd.to_numeric(df_port["weight_pct"], errors='coerce')
df_port["market_value_cr"] = pd.to_numeric(df_port["market_value_cr"], errors='coerce')
df_port["current_price_inr"] = pd.to_numeric(df_port["current_price_inr"], errors='coerce')
df_port["portfolio_date"] = pd.to_datetime(df_port["portfolio_date"]).dt.strftime('%Y-%m-%d')
df_port.to_csv(os.path.join(processed_dir, "09_portfolio_holdings.csv"), index=False)

# 10. Clean 10_benchmark_indices.csv
print("Cleaning 10_benchmark_indices.csv...")
df_bench = pd.read_csv(os.path.join(raw_dir, "10_benchmark_indices.csv"))
df_bench["date"] = pd.to_datetime(df_bench["date"]).dt.strftime('%Y-%m-%d')
df_bench["close_value"] = pd.to_numeric(df_bench["close_value"], errors='coerce')
df_bench.to_csv(os.path.join(processed_dir, "10_benchmark_indices.csv"), index=False)

print("Data cleaning completed successfully.")
