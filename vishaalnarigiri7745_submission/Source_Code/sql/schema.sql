-- Bluestock Mutual Fund Database Schema
-- Normalised 8-table Star Schema for Fintech Analytics

-- 1. Dimension: Fund Metadata
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT NOT NULL,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- 2. Dimension: Date Calendar Lookup
CREATE TABLE IF NOT EXISTS dim_date (
    date TEXT PRIMARY KEY, -- 'YYYY-MM-DD'
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    is_weekday INTEGER NOT NULL -- 1 for Mon-Fri, 0 for Sat-Sun
);

-- 3. Fact: Daily Net Asset Value (NAV)
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER,
    date TEXT,
    nav REAL NOT NULL,
    daily_return_pct REAL,
    PRIMARY KEY (amfi_code, date),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date) REFERENCES dim_date(date)
);

-- 4. Fact: Investor Transactions
CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    amfi_code INTEGER,
    transaction_date TEXT,
    transaction_type TEXT NOT NULL, -- SIP, Lumpsum, Redemption
    amount_inr REAL NOT NULL,
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
);

-- 5. Fact: Scheme Return and Risk Performance
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    morningstar_rating INTEGER,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 6. Fact: Fund Portfolio Holdings
CREATE TABLE IF NOT EXISTS fact_portfolio (
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code INTEGER,
    stock_symbol TEXT NOT NULL,
    stock_name TEXT,
    sector TEXT,
    weight_pct REAL NOT NULL,
    market_value_cr REAL,
    current_price_inr REAL,
    portfolio_date TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (portfolio_date) REFERENCES dim_date(date)
);

-- 7. Fact: Quarterly Assets Under Management (AUM) by AMC
CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    fund_house TEXT NOT NULL,
    aum_lakh_crore REAL,
    aum_crore INTEGER,
    num_schemes INTEGER
);

-- 8. Fact: Monthly Industry SIP Inflow Trends
CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month TEXT PRIMARY KEY, -- 'YYYY-MM'
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- Add indexes for fast lookup and join performance
CREATE INDEX IF NOT EXISTS idx_nav_amfi_date ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_tx_amfi_date ON fact_transactions(amfi_code, transaction_date);
CREATE INDEX IF NOT EXISTS idx_port_amfi ON fact_portfolio(amfi_code);
