# Bluestock Mutual Fund Analytics Platform
### End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard

This repository contains the complete codebase and deliverables for the Bluestock Mutual Fund Capstone Project. It constructs an automated data engineering pipeline, database design, exploratory data analysis, quantitative risk analytics, and an interactive web-based dashboard using Python, SQL, and Streamlit.

---

## 📁 Project Directory Structure

```text
bluestock/
├── data/
│   ├── raw/                      # Raw downloaded CSV files (01 to 10)
│   └── processed/                # Cleaned, structured, and computed datasets
├── db/                           # SQLite database (bluestock_mf.db)
├── notebooks/                    # Jupyter notebooks for EDA and advanced analysis
│   └── EDA_Analysis.ipynb        # Comprehensive EDA notebook with 15+ charts
├── scripts/                      # Core ETL, fetching, metrics, and recommender scripts
│   ├── inspect_data.py           # Day 1 Data Ingestion statistics generator
│   ├── validate_ingestion.py     # Master/NAV schema validation check
│   ├── live_nav_fetch.py         # REST API fetcher for mfapi.in
│   ├── data_cleaning.py          # Data cleaner (reindexing, forward-filling gaps)
│   ├── load_db.py                # Database loader using SQLAlchemy
│   ├── compute_metrics.py        # CAGR, Sharpe, Sortino, Alpha, Beta, Drawdown, VaR, CVaR
│   ├── advanced_analytics.py     # Churn predictions, cohorts, and portfolio HHI metrics
│   └── recommender.py            # Investor risk-grade matching engine
├── sql/                          # Schema definition and analytical queries
│   ├── schema.sql                # Normalised 8-table Star Schema statements
│   └── queries.sql               # 10 core business queries
├── dashboard/                    # Interactive BI dashboard
│   └── app.py                    # Multi-page Streamlit dashboard application
├── reports/                      # Documented summaries and reports
│   ├── charts/                   # Saved chart PNGs from the EDA notebook
│   ├── data_quality_summary.md   # Day 1 Data Quality inspection report
│   ├── Project_Report.pdf        # Professional multi-page project PDF report
│   └── Presentation.pptx         # 12-slide PowerPoint presentation deck
├── requirements.txt              # Project dependencies
├── run_pipeline.py               # Master orchestration script
└── README.md                     # Setup and running instructions (This file)
```

---

## ⚙️ How to Setup & Run

### 1. Prerequisites
Ensure you have Python 3.9+ installed.

### 2. Install Dependencies
Install all quantitative, visual, and reporting packages:
```bash
pip install -r requirements.txt
```

### 3. Run the Complete ETL & Engineering Pipeline
To execute all stages (data cleaning, SQLite loading, metric computations, advanced analytics, PDF compiling, and PowerPoint slide generation) in a single command, run the master script:
```bash
python run_pipeline.py
```
*Outputs generated:*
- Database initialized: `db/bluestock_mf.db`
- Metrics computed: `data/processed/fund_scorecard.csv`, `cohort_analysis.csv`, `sip_continuity.csv`, `sector_hhi.csv`
- PDF Report generated: `reports/Project_Report.pdf`
- PowerPoint deck compiled: `reports/Presentation.pptx`

### 4. Run the SQL Queries
You can run the SQL analytics directly using SQLite:
```bash
sqlite3 db/bluestock_mf.db < sql/queries.sql
```
Alternatively, execute the Python query verifier:
```bash
python scripts/execute_queries.py
```

### 5. Launch the Streamlit Interactive Dashboard
Run the multi-page dashboard application:
```bash
streamlit run dashboard/app.py
```
*Features:*
- **Page 1: Industry Overview**: Industry AUM, active SIP inflows, and top AMC metrics.
- **Page 2: Fund Performance**: Interactive bubble charts (Volatility vs Returns), scorecard filters, and fund NAV vs benchmark comparison lines.
- **Page 3: Investor Analytics**: State-wise maps/charts, payment channels, and ticket size vs age groups.
- **Page 4: SIP & Market Trends**: Dual-axis charts of SIP inflows vs Nifty 50 close price, and net category inflows heatmap.

---

## 📊 Summary of Quantitative Ratios & Models

1. **CAGR**: Compounded annual return calculated for 1-year, 3-year, and 5-year periods.
2. **Sharpe Ratio**: Risk-adjusted returns relative to a 6.5% risk-free rate proxy.
3. **Sortino Ratio**: Volatility check penalizing only negative daily returns.
4. **Alpha & Beta**: Slope/intercept regression of daily returns against corresponding category benchmarks (Nifty 50, Nifty 100, Nifty Midcap 150, BSE SmallCap).
5. **Value at Risk (95% Daily VaR)**: Calculates worst-case daily losses at a 95% confidence level.
6. **SIP Churn Continuity Model**: Identifies investors with systematic transaction gaps exceeding 35 days, flagging them as "at-risk".
7. **HHI Portfolio Concentration**: Computes Herfindahl-Hirschman Index of sector weights in portfolio holdings.
8. **Recommendation Engine**: Maps client profiles (Low/Moderate/High risk) to top suitable funds ranked by Sharpe.
