import os
import sqlite3
import pandas as pd
import numpy as np
from scipy.stats import linregress

db_path = "/Users/vaishnavnarigiri/Desktop/bluestock/db/bluestock_mf.db"
processed_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/processed"
os.makedirs(processed_dir, exist_ok=True)

# Risk-free rate (6.5% RBI repo rate proxy)
RF_RATE = 0.065
RF_DAILY = RF_RATE / 252.0

# Benchmark index mapping
benchmark_mapping = {
    'NIFTY 100 TRI': 'NIFTY100',
    'BSE 250 SmallCap TRI': 'BSE_SMALLCAP',
    'CRISIL Dynamic Gilt Index': 'CRISIL_GILT',
    'NIFTY Midcap 150 TRI': 'NIFTY_MIDCAP150',
    'CRISIL Short Term Bond Index': 'CRISIL_GILT',
    'NIFTY 500 TRI': 'NIFTY500',
    'CRISIL Liquid Fund AI Index': 'CRISIL_LIQUID',
    'NIFTY 50 TRI': 'NIFTY50',
    'NIFTY Midcap 50 TRI': 'NIFTY_MIDCAP150',
    'NIFTY Large Midcap 250 TRI': 'NIFTY100'
}

print("Loading data from database for performance calculations...")
conn = sqlite3.connect(db_path)
df_funds = pd.read_sql_query("SELECT * FROM dim_fund", conn)
df_nav = pd.read_sql_query("SELECT * FROM fact_nav", conn)
df_bench = pd.read_sql_query("SELECT * FROM clean_benchmark_indices", conn)
df_port = pd.read_sql_query("SELECT * FROM fact_portfolio", conn)
conn.close()

# Format dates
df_nav["date"] = pd.to_datetime(df_nav["date"])
df_bench["date"] = pd.to_datetime(df_bench["date"])

# Precompute benchmark returns
print("Computing benchmark returns...")
df_bench.sort_values(by=["index_name", "date"], inplace=True)
df_bench["daily_return"] = df_bench.groupby("index_name")["close_value"].pct_change()
df_bench["daily_return"].fillna(0.0, inplace=True)

# Pivot benchmark returns
bench_pivot = df_bench.pivot(index="date", columns="index_name", values="daily_return").fillna(0.0)

metrics_list = []

print("Calculating metrics for 40 funds...")
for idx, fund in df_funds.iterrows():
    amfi_code = fund["amfi_code"]
    scheme_name = fund["scheme_name"]
    fund_house = fund["fund_house"]
    expense_ratio = fund["expense_ratio_pct"]
    bench_name = fund["benchmark"]
    
    # Get fund NAV history
    fund_nav = df_nav[df_nav["amfi_code"] == amfi_code].sort_values("date").copy()
    if len(fund_nav) < 10:
        print(f"Skipping {scheme_name} (insufficient NAV history: {len(fund_nav)} rows)")
        continue
        
    # Calculate daily returns
    fund_nav["daily_return"] = fund_nav["nav"].pct_change()
    fund_nav["daily_return"].fillna(0.0, inplace=True)
    
    # CAGR Calculations
    nav_end = fund_nav.iloc[-1]["nav"]
    date_end = fund_nav.iloc[-1]["date"]
    
    # 1 Year CAGR
    date_1yr = date_end - pd.DateOffset(years=1)
    nav_1yr_df = fund_nav[fund_nav["date"] <= date_1yr]
    nav_start_1yr = nav_1yr_df.iloc[-1]["nav"] if not nav_1yr_df.empty else fund_nav.iloc[0]["nav"]
    cagr_1yr = (nav_end / nav_start_1yr) - 1.0
    
    # 3 Year CAGR
    date_3yr = date_end - pd.DateOffset(years=3)
    nav_3yr_df = fund_nav[fund_nav["date"] <= date_3yr]
    nav_start_3yr = nav_3yr_df.iloc[-1]["nav"] if not nav_3yr_df.empty else fund_nav.iloc[0]["nav"]
    cagr_3yr = (nav_end / nav_start_3yr) ** (1.0 / 3.0) - 1.0
    
    # 5 Year CAGR (or max history available)
    nav_start_5yr = fund_nav.iloc[0]["nav"]
    date_start_5yr = fund_nav.iloc[0]["date"]
    years_diff = (date_end - date_start_5yr).days / 365.25
    cagr_5yr = (nav_end / nav_start_5yr) ** (1.0 / years_diff) - 1.0
    
    # Annualised Return (based on all data)
    n_days = len(fund_nav)
    ann_return = (1 + fund_nav["daily_return"]).prod() ** (252.0 / n_days) - 1.0
    
    # Annualised Standard Deviation
    std_dev_ann = fund_nav["daily_return"].std() * np.sqrt(252.0)
    
    # Sharpe Ratio
    sharpe = (ann_return - RF_RATE) / std_dev_ann if std_dev_ann > 0 else 0.0
    
    # Sortino Ratio
    negative_returns = fund_nav["daily_return"][fund_nav["daily_return"] < 0]
    downside_std_ann = negative_returns.std() * np.sqrt(252.0)
    sortino = (ann_return - RF_RATE) / downside_std_ann if downside_std_ann > 0 else 0.0
    
    # Max Drawdown & Date Range
    fund_nav["running_max"] = fund_nav["nav"].cummax()
    fund_nav["drawdown"] = (fund_nav["nav"] - fund_nav["running_max"]) / fund_nav["running_max"]
    max_dd = fund_nav["drawdown"].min()
    
    if not fund_nav.empty and max_dd < 0:
        trough_idx = fund_nav["drawdown"].idxmin()
        trough_row = fund_nav.loc[trough_idx]
        trough_date = trough_row["date"].strftime('%Y-%m-%d') if hasattr(trough_row["date"], 'strftime') else str(trough_row["date"])
        
        # Peak date is the date of the running max at the trough
        peak_val = fund_nav.loc[trough_idx, "running_max"]
        peak_df = fund_nav[(fund_nav["date"] <= trough_row["date"]) & (fund_nav["nav"] == peak_val)]
        if not peak_df.empty:
            peak_date = peak_df.iloc[-1]["date"]
            peak_date = peak_date.strftime('%Y-%m-%d') if hasattr(peak_date, 'strftime') else str(peak_date)
        else:
            peak_date = fund_nav.iloc[0]["date"]
            peak_date = peak_date.strftime('%Y-%m-%d') if hasattr(peak_date, 'strftime') else str(peak_date)
            
        # Recovery date is the first date after trough where NAV >= peak_val
        recovery_df = fund_nav[(fund_nav["date"] > trough_row["date"]) & (fund_nav["nav"] >= peak_val)]
        if not recovery_df.empty:
            rec_date = recovery_df.iloc[0]["date"]
            recovery_date = rec_date.strftime('%Y-%m-%d') if hasattr(rec_date, 'strftime') else str(rec_date)
        else:
            recovery_date = "Not Recovered"
    else:
        peak_date = "N/A"
        trough_date = "N/A"
        recovery_date = "N/A"
        
    # Alpha & Beta vs Nifty 100 (specifically NIFTY100 index returns)
    aligned_df_nifty = pd.merge(fund_nav[["date", "daily_return"]], bench_pivot[["NIFTY100"]], left_on="date", right_index=True)
    if len(aligned_df_nifty) > 10:
        slope_n, intercept_n, r_val_n, p_val_n, std_err_n = linregress(aligned_df_nifty["NIFTY100"], aligned_df_nifty["daily_return"])
        beta_nifty = slope_n
        alpha_nifty = intercept_n * 252.0  # Annualise
        r_squared_nifty = r_val_n ** 2
    else:
        beta_nifty = 1.0
        alpha_nifty = 0.0
        r_squared_nifty = 0.0

    # Also compute Alpha & Beta vs fund's specific mapped benchmark (for dashboard backwards compatibility)
    mapped_bench = benchmark_mapping.get(bench_name, "NIFTY100")
    aligned_df = pd.merge(fund_nav[["date", "daily_return"]], bench_pivot[[mapped_bench]], left_on="date", right_index=True)
    if len(aligned_df) > 10:
        slope, intercept, r_val, p_val, std_err = linregress(aligned_df[mapped_bench], aligned_df["daily_return"])
        beta = slope
        alpha = intercept * 252.0
    else:
        beta = 1.0
        alpha = 0.0
        
    # Value at Risk (VaR 95% Daily) and CVaR
    var_95_daily = np.percentile(fund_nav["daily_return"], 5)
    cvar_95_daily = fund_nav["daily_return"][fund_nav["daily_return"] <= var_95_daily].mean()
    
    # Herfindahl-Hirschman Index (HHI) for Sector Concentration
    fund_port = df_port[df_port["amfi_code"] == amfi_code]
    if not fund_port.empty:
        sector_weights = fund_port.groupby("sector")["weight_pct"].sum() / 100.0
        hhi = (sector_weights ** 2).sum()
    else:
        hhi = 0.0
        
    metrics_list.append({
        "amfi_code": amfi_code,
        "scheme_name": scheme_name,
        "fund_house": fund_house,
        "expense_ratio_pct": expense_ratio,
        "return_1yr_pct": cagr_1yr * 100.0,
        "return_3yr_pct": cagr_3yr * 100.0,
        "return_5yr_pct": cagr_5yr * 100.0,
        "annualised_return_pct": ann_return * 100.0,
        "std_dev_ann_pct": std_dev_ann * 100.0,
        "sharpe_ratio": sharpe,
        "sortino_ratio": sortino,
        "max_drawdown_pct": max_dd * 100.0,
        "drawdown_peak_date": peak_date,
        "drawdown_trough_date": trough_date,
        "drawdown_recovery_date": recovery_date,
        "beta": beta_nifty,  # Use Nifty 100 beta as primary
        "alpha": alpha_nifty * 100.0,  # Use Nifty 100 alpha as primary (in percentage)
        "beta_bench": beta,  # Specific benchmark beta
        "alpha_bench": alpha * 100.0,  # Specific benchmark alpha
        "var_95_daily_pct": var_95_daily * 100.0,
        "cvar_95_daily_pct": cvar_95_daily * 100.0,
        "sector_hhi": hhi,
        "r_squared_nifty": r_squared_nifty
    })

df_metrics = pd.DataFrame(metrics_list)

# Load original performance dataset to retrieve AUM
df_orig_perf = pd.read_csv("/Users/vaishnavnarigiri/Desktop/bluestock/data/raw/07_scheme_performance.csv")
df_metrics["aum_crore"] = df_metrics["amfi_code"].map(dict(zip(df_orig_perf["amfi_code"], df_orig_perf["aum_crore"])))
df_metrics["morningstar_rating"] = df_metrics["amfi_code"].map(dict(zip(df_orig_perf["amfi_code"], df_orig_perf["morningstar_rating"])))

# Build Scorecard ranks (0 to 100 percentiles)
df_metrics["rank_return"] = df_metrics["return_3yr_pct"].rank(pct=True) * 100.0
df_metrics["rank_sharpe"] = df_metrics["sharpe_ratio"].rank(pct=True) * 100.0
df_metrics["rank_alpha"] = df_metrics["alpha"].rank(pct=True) * 100.0
df_metrics["rank_expense"] = df_metrics["expense_ratio_pct"].rank(ascending=False, pct=True) * 100.0
df_metrics["rank_drawdown"] = df_metrics["max_drawdown_pct"].rank(ascending=True, pct=True) * 100.0 # less negative is better

# Score = 30%*Return + 25%*Sharpe + 20%*Alpha + 15%*Expense + 10%*Drawdown
df_metrics["composite_score"] = (
    0.30 * df_metrics["rank_return"] +
    0.25 * df_metrics["rank_sharpe"] +
    0.20 * df_metrics["rank_alpha"] +
    0.15 * df_metrics["rank_expense"] +
    0.10 * df_metrics["rank_drawdown"]
)

# Output CSV: Scorecard
df_metrics.sort_values(by="composite_score", ascending=False, inplace=True)
scorecard_path = os.path.join(processed_dir, "fund_scorecard.csv")
df_metrics.to_csv(scorecard_path, index=False)
print(f"Fund scorecard saved to {scorecard_path}")

# Output CSV: Alpha & Beta vs Nifty 100
alpha_beta_df = df_metrics[["amfi_code", "scheme_name", "alpha", "beta", "r_squared_nifty"]].copy()
alpha_beta_df.rename(columns={"alpha": "alpha_pct", "r_squared_nifty": "r_squared"}, inplace=True)
alpha_beta_path = os.path.join(processed_dir, "alpha_beta.csv")
alpha_beta_df.to_csv(alpha_beta_path, index=False)
print(f"Alpha-Beta report saved to {alpha_beta_path}")

# Load updated scorecard back into SQLite database
print("Updating SQLite table 'fact_performance'...")
conn = sqlite3.connect(db_path)
# Clean columns for SQLite representation
db_perf_cols = [
    "amfi_code", "return_1yr_pct", "return_3yr_pct", "return_5yr_pct",
    "alpha", "beta", "sharpe_ratio", "sortino_ratio", "std_dev_ann_pct",
    "max_drawdown_pct", "morningstar_rating", "aum_crore", "composite_score"
]
df_db_perf = df_metrics[db_perf_cols].copy()
df_db_perf.to_sql("fact_performance", conn, if_exists="replace", index=False)
conn.close()
print("SQLite database table 'fact_performance' updated successfully.")

