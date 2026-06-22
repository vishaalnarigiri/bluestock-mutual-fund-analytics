import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine

# Database path
db_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/db"
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "bluestock_mf.db")
schema_path = "/Users/vaishnavnarigiri/Desktop/bluestock/sql/schema.sql"
processed_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/processed"

# Initialize SQLAlchemy engine
engine = create_engine(f"sqlite:///{db_path}")

print("Initializing database schema...")
# Execute schema.sql to create tables
with sqlite3.connect(db_path) as conn:
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
print("Database tables created.")

# 1. Populate dim_date
print("Generating dim_date dimension data...")
all_dates = pd.date_range(start='2021-12-01', end='2026-06-30', freq='D')
df_date = pd.DataFrame({
    'date': all_dates.strftime('%Y-%m-%d'),
    'year': all_dates.year,
    'month': all_dates.month,
    'quarter': all_dates.quarter,
    'day_of_week': all_dates.dayofweek, # 0=Monday, 6=Sunday
    'is_weekday': (all_dates.dayofweek < 5).astype(int)
})
df_date.to_sql('dim_date', engine, if_exists='replace', index=False)
print("Successfully loaded dim_date.")

# Helper to load CSV into table
def load_csv_to_db(csv_filename, table_name, calculate_returns=False):
    file_path = os.path.join(processed_dir, csv_filename)
    if not os.path.exists(file_path):
        print(f"Skipping {csv_filename} (file does not exist).")
        return
        
    df = pd.read_csv(file_path)
    
    if calculate_returns and table_name == "fact_nav":
        print(f"Computing daily returns for {table_name}...")
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values(by=["amfi_code", "date"], inplace=True)
        # Percent change returns
        df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
        df["daily_return_pct"] = df["daily_return_pct"].fillna(0.0)
        df["date"] = df["date"].dt.strftime('%Y-%m-%d')
        
    print(f"Loading {csv_filename} into table '{table_name}'...")
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Successfully loaded {len(df)} rows into '{table_name}'.")

# Load all datasets
load_csv_to_db("01_fund_master.csv", "dim_fund")
load_csv_to_db("02_nav_history.csv", "fact_nav", calculate_returns=True)
load_csv_to_db("08_investor_transactions.csv", "fact_transactions")
load_csv_to_db("07_scheme_performance.csv", "fact_performance")
load_csv_to_db("09_portfolio_holdings.csv", "fact_portfolio")
load_csv_to_db("03_aum_by_fund_house.csv", "fact_aum")
load_csv_to_db("04_monthly_sip_inflows.csv", "fact_sip_industry")
load_csv_to_db("10_benchmark_indices.csv", "clean_benchmark_indices")

# Load category inflows and industry folio counts as facts
load_csv_to_db("05_category_inflows.csv", "fact_category_inflows")
load_csv_to_db("06_industry_folio_count.csv", "fact_industry_folios")

print("Database loading completed successfully.")
