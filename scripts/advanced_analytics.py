import os
import sqlite3
import pandas as pd
import numpy as np

db_path = "/Users/vaishnavnarigiri/Desktop/bluestock/db/bluestock_mf.db"
processed_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/processed"
os.makedirs(processed_dir, exist_ok=True)

print("Running advanced analytics pipeline...")

# 1. Connect to DB
conn = sqlite3.connect(db_path)
df_tx = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
df_funds = pd.read_sql_query("SELECT amfi_code, category, sub_category, risk_category FROM dim_fund", conn)
df_port = pd.read_sql_query("SELECT * FROM fact_portfolio", conn)
conn.close()

# Format date column
df_tx["transaction_date"] = pd.to_datetime(df_tx["transaction_date"])

# 2. Investor Cohort Analysis
print("Performing investor cohort analysis...")
# Find first transaction date for each investor
df_first_tx = df_tx.groupby("investor_id")["transaction_date"].min().reset_index()
df_first_tx.rename(columns={"transaction_date": "first_transaction_date"}, inplace=True)
df_first_tx["cohort_year"] = df_first_tx["first_transaction_date"].dt.year

# Merge cohort information back to transaction log
df_tx_cohort = pd.merge(df_tx, df_first_tx[["investor_id", "cohort_year"]], on="investor_id")
df_tx_cohort = pd.merge(df_tx_cohort, df_funds, on="amfi_code")

# Aggregate cohort behaviors
cohort_summary = df_tx_cohort.groupby("cohort_year").agg(
    total_investors=("investor_id", "nunique"),
    total_invested_inr=("amount_inr", "sum"),
    avg_ticket_size=("amount_inr", "mean"),
    total_transactions=("investor_id", "count"),
    sip_transactions=("transaction_type", lambda x: (x == "SIP").sum()),
    redemption_transactions=("transaction_type", lambda x: (x == "Redemption").sum())
).reset_index()

# Calculate average SIP amount per cohort
df_sip_only = df_tx_cohort[df_tx_cohort["transaction_type"] == "SIP"]
cohort_sip_avg = df_sip_only.groupby("cohort_year")["amount_inr"].mean().reset_index()
cohort_sip_avg.rename(columns={"amount_inr": "avg_sip_amount_inr"}, inplace=True)

cohort_summary = pd.merge(cohort_summary, cohort_sip_avg, on="cohort_year")
cohort_path = os.path.join(processed_dir, "cohort_analysis.csv")
cohort_summary.to_csv(cohort_path, index=False)
print(f"Cohort analysis saved to {cohort_path}")

# 3. SIP Continuity / Churn Analysis
print("Performing SIP continuity analysis...")
# For each investor with 6+ SIP transactions, compute average gap between transactions
df_sip_tx = df_tx[df_tx["transaction_type"] == "SIP"].sort_values(by=["investor_id", "transaction_date"]).copy()
df_sip_count = df_sip_tx.groupby("investor_id").size().reset_index(name="sip_count")
loyal_sip_investors = df_sip_count[df_sip_count["sip_count"] >= 6]["investor_id"]

sip_continuity_list = []
for inv_id in loyal_sip_investors:
    inv_tx = df_sip_tx[df_sip_tx["investor_id"] == inv_id].copy()
    inv_tx["gap_days"] = inv_tx["transaction_date"].diff().dt.days
    
    avg_gap = inv_tx["gap_days"].mean()
    max_gap = inv_tx["gap_days"].max()
    
    # Flag as 'at-risk' if any gap exceeded 35 days (meaning they missed/delayed a monthly payment cycle)
    at_risk_flag = 1 if max_gap > 35 else 0
    
    sip_continuity_list.append({
        "investor_id": inv_id,
        "sip_count": len(inv_tx),
        "average_gap_days": avg_gap,
        "max_gap_days": max_gap,
        "is_at_risk": at_risk_flag
    })

df_continuity = pd.DataFrame(sip_continuity_list)
continuity_path = os.path.join(processed_dir, "sip_continuity.csv")
df_continuity.to_csv(continuity_path, index=False)
print(f"SIP continuity report saved to {continuity_path}")
print(f"Total at-risk investors flagged: {df_continuity['is_at_risk'].sum()} out of {len(df_continuity)}")

# 4. Sector Concentration (HHI) Report
print("Performing portfolio sector concentration analysis...")
df_port_merged = pd.merge(df_port, df_funds, on="amfi_code")
# Calculate HHI per scheme
hhi_list = []
for amfi, group in df_port_merged.groupby("amfi_code"):
    weights = group["weight_pct"] / 100.0
    hhi = (weights ** 2).sum()
    hhi_list.append({
        "amfi_code": amfi,
        "sector_hhi": hhi,
        "top_sector": group.groupby("sector")["weight_pct"].sum().idxmax(),
        "top_sector_weight_pct": group.groupby("sector")["weight_pct"].sum().max()
    })
df_hhi = pd.DataFrame(hhi_list)
hhi_path = os.path.join(processed_dir, "sector_hhi.csv")
df_hhi.to_csv(hhi_path, index=False)
print(f"Sector HHI report saved to {hhi_path}")

print("Advanced analytics completed successfully.")
