import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

db_path = "/Users/vaishnavnarigiri/Desktop/bluestock/db/bluestock_mf.db"
processed_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/processed"
charts_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/reports/charts"
os.makedirs(charts_dir, exist_ok=True)

# 1. Load scorecard and identify top 5 funds
scorecard = pd.read_csv(os.path.join(processed_dir, "fund_scorecard.csv"))
top_5_funds = scorecard.head(5)
top_5_amfi = top_5_funds["amfi_code"].tolist()
top_5_names = top_5_funds["scheme_name"].tolist()
# Clean names for plotting legend
top_5_legends = [name.split(" - ")[0] for name in top_5_names]
amfi_to_legend = dict(zip(top_5_amfi, top_5_legends))

# 2. Connect to database and retrieve NAV/indices data
conn = sqlite3.connect(db_path)
df_nav = pd.read_sql_query("SELECT * FROM fact_nav WHERE amfi_code IN ({})".format(",".join(map(str, top_5_amfi))), conn)
df_bench = pd.read_sql_query("SELECT * FROM clean_benchmark_indices WHERE index_name IN ('NIFTY50', 'NIFTY100')", conn)
conn.close()

# Convert dates to datetime
df_nav["date"] = pd.to_datetime(df_nav["date"])
df_bench["date"] = pd.to_datetime(df_bench["date"])

# 3. Define 3-year window based on the latest date in NAV history
end_date = df_nav["date"].max()
start_date = end_date - pd.DateOffset(years=3)

# Filter NAV and benchmarks to the last 3 years
df_nav_3y = df_nav[(df_nav["date"] >= start_date) & (df_nav["date"] <= end_date)].copy()
df_bench_3y = df_bench[(df_bench["date"] >= start_date) & (df_bench["date"] <= end_date)].copy()

# Pivot benchmarks
bench_pivot = df_bench_3y.pivot(index="date", columns="index_name", values="close_value")

# Prepare plot
plt.figure(figsize=(12, 7))
sns.set_theme(style="whitegrid")

tracking_errors = []

# Normalize and plot Nifty 50 and Nifty 100
nifty50_series = bench_pivot["NIFTY50"].dropna().sort_index()
nifty100_series = bench_pivot["NIFTY100"].dropna().sort_index()

nifty50_norm = (nifty50_series / nifty50_series.iloc[0]) * 100.0
nifty100_norm = (nifty100_series / nifty100_series.iloc[0]) * 100.0

plt.plot(nifty50_norm.index, nifty50_norm.values, label="NIFTY 50 (Benchmark)", color="#2563eb", linewidth=2.5, linestyle="--")
plt.plot(nifty100_norm.index, nifty100_norm.values, label="NIFTY 100 (Benchmark)", color="#4b5563", linewidth=2.5, linestyle=":")

# Compute daily returns for benchmarks to use in tracking error
nifty50_returns = nifty50_series.pct_change().fillna(0.0)
nifty100_returns = nifty100_series.pct_change().fillna(0.0)

# Normalize and plot each of the top 5 funds
for amfi in top_5_amfi:
    fund_data = df_nav_3y[df_nav_3y["amfi_code"] == amfi].sort_values("date").copy()
    if fund_data.empty:
        continue
    
    fund_series = fund_data.set_index("date")["nav"]
    fund_norm = (fund_series / fund_series.iloc[0]) * 100.0
    
    plt.plot(fund_norm.index, fund_norm.values, label=amfi_to_legend[amfi], linewidth=2.0)
    
    # Compute Tracking Error vs Nifty 50 and Nifty 100
    fund_returns = fund_series.pct_change().fillna(0.0)
    
    # Align fund and benchmark daily returns
    aligned_50 = pd.merge(fund_returns.to_frame("fund"), nifty50_returns.to_frame("bench"), left_index=True, right_index=True)
    aligned_100 = pd.merge(fund_returns.to_frame("fund"), nifty100_returns.to_frame("bench"), left_index=True, right_index=True)
    
    te_n50 = np.std(aligned_50["fund"] - aligned_50["bench"]) * np.sqrt(252)
    te_n100 = np.std(aligned_100["fund"] - aligned_100["bench"]) * np.sqrt(252)
    
    tracking_errors.append({
        "amfi_code": amfi,
        "scheme_name": scorecard[scorecard["amfi_code"] == amfi].iloc[0]["scheme_name"],
        "tracking_error_vs_nifty50_pct": te_n50 * 100.0,
        "tracking_error_vs_nifty100_pct": te_n100 * 100.0
    })

# Format plot
plt.title("Top 5 Funds vs. Benchmarks (Normalized 3-Year Growth, Start = 100)", fontsize=14, fontweight="bold", pad=15)
plt.xlabel("Date", fontsize=12, labelpad=10)
plt.ylabel("Normalized NAV / Index Value", fontsize=12, labelpad=10)
plt.legend(loc="upper left", frameon=True, facecolor="white", edgecolor="none", fontsize=10)
plt.tight_layout()

# Save the plot
plot_path = os.path.join(charts_dir, "benchmark_comparison.png")
plt.savefig(plot_path, dpi=300)
plt.close()
print(f"Benchmark comparison chart saved to {plot_path}")

# Output Tracking Errors to CSV
df_te = pd.DataFrame(tracking_errors)
te_path = os.path.join(processed_dir, "tracking_error.csv")
df_te.to_csv(te_path, index=False)
print(f"Tracking error report saved to {te_path}")
