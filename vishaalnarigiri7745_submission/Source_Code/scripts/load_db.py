import os
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, event

# Database path
db_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/db"
os.makedirs(db_dir, exist_ok=True)
db_path = os.path.join(db_dir, "bluestock_mf.db")
schema_path = "/Users/vaishnavnarigiri/Desktop/bluestock/sql/schema.sql"
processed_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/processed"

# Initialize SQLAlchemy engine
engine = create_engine(f"sqlite:///{db_path}")

# Enforce foreign key constraints in SQLAlchemy for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()

print("Initializing database schema...")
# Execute schema.sql to drop and recreate tables with full star schema constraints
with sqlite3.connect(db_path) as conn:
    conn.execute("PRAGMA foreign_keys = OFF;") # Turn off foreign keys temporarily during drop/recreate
    with open(schema_path, 'r') as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.execute("PRAGMA foreign_keys = ON;")
print("Database tables created/re-created successfully with constraints and indexes.")

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
df_date.to_sql('dim_date', engine, if_exists='append', index=False)
print("Successfully loaded dim_date.")

# Helper to load CSV into table
def load_csv_to_db(csv_filename, table_name, calculate_returns=False):
    file_path = os.path.join(processed_dir, csv_filename)
    if not os.path.exists(file_path):
        print(f"Skipping {csv_filename} (file does not exist).")
        return
        
    df = pd.read_csv(file_path)
    csv_row_count = len(df)
    
    if calculate_returns and table_name == "fact_nav":
        print(f"Computing daily returns for {table_name}...")
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values(by=["amfi_code", "date"], inplace=True)
        # Percent change returns
        df["daily_return_pct"] = df.groupby("amfi_code")["nav"].pct_change() * 100
        df["daily_return_pct"] = df["daily_return_pct"].fillna(0.0)
        df["date"] = df["date"].dt.strftime('%Y-%m-%d')
        
    print(f"Loading {csv_filename} into table '{table_name}'...")
    
    # Retrieve columns from SQLite schema to filter df columns
    # This prevents SQLAlchemy from dropping/replacing and ensures columns match the schema exactly.
    from sqlalchemy import inspect
    inspector = inspect(engine)
    try:
        table_columns = [col['name'] for col in inspector.get_columns(table_name)]
        # Filter dataframe columns to only keep those defined in the schema
        # (ignoring auto-increment key columns like tx_id, portfolio_id, aum_id, etc. if they are not in df)
        insert_cols = [c for c in table_columns if c in df.columns]
        df_to_insert = df[insert_cols]
    except Exception as e:
        print(f"Warning: Could not get table info for '{table_name}', inserting all columns. Error: {e}")
        df_to_insert = df

    # Use if_exists='append' to preserve the schema (primary/foreign keys and indexes)
    df_to_insert.to_sql(table_name, engine, if_exists='append', index=False)
    
    # Verify row counts
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        db_row_count = cursor.fetchone()[0]
    
    print(f"Verification: CSV has {csv_row_count} rows. SQLite table '{table_name}' has {db_row_count} rows.")
    if csv_row_count == db_row_count:
        print(f"✓ Success: Row counts match for '{table_name}'!")
    else:
        print(f"⚠ Warning: Row count mismatch for '{table_name}'! (CSV: {csv_row_count}, DB: {db_row_count})")

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
