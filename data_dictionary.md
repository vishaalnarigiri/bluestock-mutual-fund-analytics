# Bluestock Mutual Fund Analytics: Data Dictionary

This data dictionary documents the database tables, schemas, columns, data types, constraints, business definitions, and source files of the 11 tables in the SQLite database (`bluestock_mf.db`) designed for the Capstone Project.

---

## 🗂️ Star Schema Table Catalog

### 1. `dim_fund` (Fund Dimension)
* **Description**: Contains master metadata for all mutual fund schemes analyzed on the platform.
* **Source**: `data/processed/01_fund_master.csv`
* **Grain**: One row per AMFI Scheme Code (`amfi_code`).

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY | Association of Mutual Funds in India (AMFI) code uniquely identifying each scheme. |
| `fund_house` | TEXT | NOT NULL | Asset Management Company (AMC) managing the fund (e.g., SBI Mutual Fund, Axis Mutual Fund). |
| `scheme_name` | TEXT | NOT NULL | The official name of the mutual fund scheme. |
| `category` | TEXT | NOT NULL | Asset class category (e.g., Equity, Debt, Hybrid). |
| `sub_category` | TEXT | | Underlying investment strategy style (e.g., Large Cap, Mid Cap, Flexi Cap). |
| `plan` | TEXT | | Plan structure of the scheme (e.g., Direct, Regular). |
| `launch_date` | TEXT | | Launch date of the fund formatted as `YYYY-MM-DD`. |
| `benchmark` | TEXT | | Standard index used to measure fund performance (e.g., Nifty 50, BSE SmallCap). |
| `expense_ratio_pct` | REAL | | Annual management fee charged as a percentage of AUM. |
| `exit_load_pct` | REAL | | Fee charged to investors when redeeming units early, as a percentage. |
| `min_sip_amount` | REAL | | Minimum transaction size required for Systematic Investment Plan. |
| `min_lumpsum_amount` | REAL | | Minimum transaction size required for a one-off lumpsum purchase. |
| `fund_manager` | TEXT | | Name of the primary manager handling portfolio investments. |
| `risk_category` | TEXT | | Standardized risk category (e.g., Very High, Moderately High). |
| `sebi_category_code` | TEXT | | SEBI standardized category code for regulatory compliance. |

---

### 2. `dim_date` (Date Dimension)
* **Description**: Calendar lookup dimension supporting time-series aggregation, filtering, and joining.
* **Source**: Generated programmatically from date ranges (Dec 2021 to June 2026).
* **Grain**: One row per calendar date.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | PRIMARY KEY | Calendar date in `YYYY-MM-DD` format. |
| `year` | INTEGER | NOT NULL | Calendar year (e.g., 2024). |
| `month` | INTEGER | NOT NULL | Calendar month index (1 to 12). |
| `quarter` | INTEGER | NOT NULL | Calendar quarter index (1 to 4). |
| `day_of_week` | INTEGER | NOT NULL | Zero-indexed day of the week (0 = Monday, 6 = Sunday). |
| `is_weekday` | INTEGER | NOT NULL | Boolean flag (1 = Mon-Fri, 0 = Sat-Sun). |

---

### 3. `fact_nav` (NAV Fact Table)
* **Description**: Daily Net Asset Value (NAV) records and daily returns for all funds.
* **Source**: `data/processed/02_nav_history.csv`
* **Grain**: One row per fund per calendar date.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY, FK | References `dim_fund(amfi_code)`. |
| `date` | TEXT | PRIMARY KEY, FK | References `dim_date(date)` in `YYYY-MM-DD` format. |
| `nav` | REAL | NOT NULL | The net asset value per unit of the scheme for the given day. |
| `daily_return_pct` | REAL | | Daily return percentage calculated as $(NAV_t - NAV_{t-1}) / NAV_{t-1} \times 100$. |

---

### 4. `fact_transactions` (Investor Transactions Fact Table)
* **Description**: Granular investor transactional database documenting subscriptions and redemptions.
* **Source**: `data/processed/08_investor_transactions.csv`
* **Grain**: One row per individual transaction.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `tx_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique autoincremented identifier for each transaction. |
| `investor_id` | TEXT | NOT NULL | Anonymized unique identifier for the investor. |
| `amfi_code` | INTEGER | FK | References `dim_fund(amfi_code)`. |
| `transaction_date` | TEXT | FK | References `dim_date(date)`. |
| `transaction_type` | TEXT | NOT NULL | Category of transactions: `SIP`, `Lumpsum`, or `Redemption`. |
| `amount_inr` | REAL | NOT NULL | Amount of transaction in Indian Rupees (INR) (must be $> 0$). |
| `state` | TEXT | | Indian state of residence for the investor. |
| `city` | TEXT | | Indian city of residence for the investor. |
| `city_tier` | TEXT | | Indian city tier (e.g., Tier 1, Tier 2). |
| `age_group` | TEXT | | Investor age bracket (e.g., 18-25, 26-35, 36-45). |
| `gender` | TEXT | | Gender identity of the investor. |
| `annual_income_lakh` | REAL | | Investor annual income stated in Lakh INR. |
| `payment_mode` | TEXT | | Payment channel (e.g., Net Banking, UPI, Mandate). |
| `kyc_status` | TEXT | | Compliance verification status (`Verified` or `Pending`). |

---

### 5. `fact_performance` (Performance Summary Fact Table)
* **Description**: Returns, risk metrics, and key performance indicators computed for each mutual fund scheme.
* **Source**: `data/processed/07_scheme_performance.csv`
* **Grain**: One row per AMFI Scheme Code (`amfi_code`).

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `amfi_code` | INTEGER | PRIMARY KEY, FK | References `dim_fund(amfi_code)`. |
| `scheme_name` | TEXT | | The official name of the mutual fund scheme. |
| `fund_house` | TEXT | | Asset Management Company (AMC) managing the fund. |
| `category` | TEXT | | Asset class category (e.g., Equity, Debt). |
| `plan` | TEXT | | Plan structure of the scheme (e.g., Direct, Regular). |
| `return_1yr_pct` | REAL | | Compounded annual return achieved over the last 1 year. |
| `return_3yr_pct` | REAL | | Compounded annual return achieved over the last 3 years. |
| `return_5yr_pct` | REAL | | Compounded annual return achieved over the last 5 years. |
| `benchmark_3yr_pct` | REAL | | Benchmark index compounded annual return over 3 years. |
| `alpha` | REAL | | Measure of excess return generated relative to the benchmark. |
| `beta` | REAL | | Measure of fund volatility relative to its category benchmark. |
| `sharpe_ratio` | REAL | | Risk-adjusted return metric relative to a 6.5% risk-free rate proxy. |
| `sortino_ratio` | REAL | | Risk-adjusted return metric penalizing only downside volatility. |
| `std_dev_ann_pct` | REAL | | Annualized standard deviation of daily returns (volatility measure). |
| `max_drawdown_pct` | REAL | | Maximum peak-to-trough decline percentage in NAV. |
| `aum_crore` | INTEGER | | Assets Under Management of the specific fund scheme in Crore INR. |
| `expense_ratio_pct` | REAL | | Management fee percentage for the scheme. |
| `morningstar_rating` | INTEGER | | Qualitative rating assigned to the fund (1 to 5 stars). |
| `risk_grade` | TEXT | | Qualitative risk classification grade. |
| `negative_sharpe_flag`| INTEGER | | Indicator flag (1 if Sharpe ratio is negative, 0 otherwise). |
| `expense_ratio_valid`| INTEGER | | Validation flag (1 if expense ratio is between 0.1% and 2.5%, 0 otherwise). |

---

### 6. `fact_portfolio` (Portfolio Holdings Fact Table)
* **Description**: Detailed underlying stock allocations held by each mutual fund scheme.
* **Source**: `data/processed/09_portfolio_holdings.csv`
* **Grain**: One row per fund per stock holding.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `portfolio_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for each portfolio holding entry. |
| `amfi_code` | INTEGER | FK | References `dim_fund(amfi_code)`. |
| `stock_symbol` | TEXT | NOT NULL | Ticker symbol of the stock on exchanges (e.g., RELIANCE, TCS). |
| `stock_name` | TEXT | | Name of the public corporation holding. |
| `sector` | TEXT | | Industrial sector division (e.g., Financial Services, IT). |
| `weight_pct` | REAL | NOT NULL | Allocation percentage of the stock within the mutual fund's portfolio. |
| `market_value_cr` | REAL | | Total current market value of the allocation in Crore INR. |
| `current_price_inr` | REAL | | Market price of a single share in INR. |
| `portfolio_date` | TEXT | FK | Date of holding statement formatted as `YYYY-MM-DD`. References `dim_date(date)`. |

---

### 7. `fact_aum` (AMC Assets Under Management Fact Table)
* **Description**: Total Assets Under Management (AUM) trends grouped quarterly per Fund House (AMC).
* **Source**: `data/processed/03_aum_by_fund_house.csv`
* **Grain**: One row per fund house per quarter end date.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `aum_id` | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier for each quarterly AUM record. |
| `date` | TEXT | NOT NULL | Quarter end date formatted as `YYYY-MM-DD`. |
| `fund_house` | TEXT | NOT NULL | Asset Management Company (AMC) name. |
| `aum_lakh_crore` | REAL | | AUM of the AMC in Lakh Crore INR. |
| `aum_crore` | INTEGER | | AUM of the AMC in Crore INR. |
| `num_schemes` | INTEGER | | Total number of schemes offered by the AMC. |

---

### 8. `fact_sip_industry` (Industry Monthly SIP Inflows Fact Table)
* **Description**: Aggregate systematic monthly investment plan metrics across the Indian mutual fund industry.
* **Source**: `data/processed/04_monthly_sip_inflows.csv`
* **Grain**: One row per calendar month.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY | Year and month index formatted as `YYYY-MM`. |
| `sip_inflow_crore` | REAL | | Aggregate SIP inflows in Crore INR for the month. |
| `active_sip_accounts_crore` | REAL | | Count of active systematic investment accounts in Crore units. |
| `new_sip_accounts_lakh` | REAL | | Number of new SIP registrations in Lakh units during the month. |
| `sip_aum_lakh_crore` | REAL | | Total industry AUM derived from systematic accounts in Lakh Crore INR. |
| `yoy_growth_pct` | REAL | | Year-over-Year growth percentage of SIP inflow. |

---

### 9. `clean_benchmark_indices` (Benchmark Indices Fact Table)
* **Description**: Daily index closing values for the standard benchmark benchmarks (e.g., Nifty 50, BSE SmallCap).
* **Source**: `data/processed/10_benchmark_indices.csv`
* **Grain**: One row per index per calendar date.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `date` | TEXT | PRIMARY KEY, FK | References `dim_date(date)`. |
| `index_name` | TEXT | PRIMARY KEY | The official index code (e.g., Nifty 50, Nifty Midcap 150). |
| `close_value` | REAL | | Closing value of the index for the day. |

---

### 10. `fact_category_inflows` (Mutual Fund Category Inflow Fact Table)
* **Description**: Monthly net financial inflows broken down by mutual fund product category.
* **Source**: `data/processed/05_category_inflows.csv`
* **Grain**: One row per category per calendar month.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY | Month of record in `YYYY-MM` format. |
| `category` | TEXT | PRIMARY KEY | Mutual fund category classification (e.g., Small Cap Fund, Liquid Fund). |
| `net_inflow_crore` | REAL | | Net inflow amount (purchases minus redemptions) in Crore INR. |

---

### 11. `fact_industry_folios` (Folio Counts Fact Table)
* **Description**: Total active investor account folios tracked across key asset classes in the mutual fund industry.
* **Source**: `data/processed/06_industry_folio_count.csv`
* **Grain**: One row per calendar month.

| Column Name | Data Type | Constraints | Business Definition / Description |
| :--- | :--- | :--- | :--- |
| `month` | TEXT | PRIMARY KEY | Month of record in `YYYY-MM` format. |
| `total_folios_crore` | REAL | | Aggregate mutual fund investor accounts (folios) in Crores. |
| `equity_folios_crore`| REAL | | Equity scheme investor accounts (folios) in Crores. |
| `debt_folios_crore`  | REAL | | Debt scheme investor accounts (folios) in Crores. |
| `hybrid_folios_crore`| REAL | | Hybrid scheme investor accounts (folios) in Crores. |
| `others_folios_crore`| REAL | | Other scheme types investor accounts (folios) in Crores. |
