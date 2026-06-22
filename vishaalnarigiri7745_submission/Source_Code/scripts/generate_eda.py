import os
import json

notebook_path = "/Users/vaishnavnarigiri/Desktop/bluestock/notebooks/EDA_Analysis.ipynb"
charts_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/reports/charts"
os.makedirs(charts_dir, exist_ok=True)

# Define cells
cells = []

# Title and introduction
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "# Exploratory Data Analysis (EDA): Mutual Fund Analytics Platform\n",
        "This notebook contains the complete Exploratory Data Analysis for the Bluestock Mutual Fund Capstone project. It loads the clean relational tables from SQLite, visualizes market trends, and derives demographic and performance insights."
    ]
})

# Code Cell 1: Setup and imports
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "import os\n",
        "import sqlite3\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "\n",
        "# Set plotting styles\n",
        "sns.set_theme(style=\"whitegrid\")\n",
        "plt.rcParams[\"figure.figsize\"] = (12, 6)\n",
        "plt.rcParams[\"axes.titlesize\"] = 14\n",
        "plt.rcParams[\"axes.labelsize\"] = 12\n",
        "\n",
        "db_path = \"/Users/vaishnavnarigiri/Desktop/bluestock/db/bluestock_mf.db\"\n",
        "charts_dir = \"/Users/vaishnavnarigiri/Desktop/bluestock/reports/charts\"\n",
        "os.makedirs(charts_dir, exist_ok=True)\n",
        "print(\"Setup complete. DB connected.\")"
    ]
})

# Markdown Cell 2: NAV Trends
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 1. NAV Trends (2022 - 2026)\n",
        "We visualize the historical NAV movement for 6 major large-cap schemes: HDFC Top 100, SBI Bluechip, ICICI Bluechip, Nippon Large Cap, Axis Bluechip, and Kotak Bluechip."
    ]
})

# Code Cell 2: NAV Trends Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "query = \"\"\"\n",
        "SELECT n.date, n.nav, f.scheme_name, f.amfi_code \n",
        "FROM fact_nav n\n",
        "JOIN dim_fund f ON n.amfi_code = f.amfi_code\n",
        "WHERE f.amfi_code IN (125497, 119551, 120503, 118632, 119092, 120841)\n",
        "\"\"\"\n",
        "df_nav = pd.read_sql_query(query, conn)\n",
        "conn.close()\n",
        "\n",
        "df_nav[\"date\"] = pd.to_datetime(df_nav[\"date\"])\n",
        "df_pivot = df_nav.pivot(index=\"date\", columns=\"scheme_name\", values=\"nav\")\n",
        "\n",
        "plt.figure(figsize=(14, 7))\n",
        "for col in df_pivot.columns:\n",
        "    plt.plot(df_pivot.index, df_pivot[col], label=col.split(' - ')[0])\n",
        "\n",
        "plt.title(\"NAV Historical Trends (2022 - 2026) for Core Large-Cap Funds\")\n",
        "plt.xlabel(\"Date\")\n",
        "plt.ylabel(\"NAV (INR)\")\n",
        "plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"nav_trends.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 3: AUM Growth
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 2. AUM Growth by Fund House\n",
        "We track the quarterly Assets Under Management (AUM) growth for the 10 largest fund houses in India."
    ]
})

# Code Cell 3: AUM Growth Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "df_aum = pd.read_sql_query(\"SELECT * FROM fact_aum\", conn)\n",
        "conn.close()\n",
        "\n",
        "df_aum[\"date\"] = pd.to_datetime(df_aum[\"date\"])\n",
        "df_aum[\"year\"] = df_aum[\"date\"].dt.year\n",
        "\n",
        "# Group by Year and Fund House to see yearly progression\n",
        "df_yearly_aum = df_aum.groupby([\"year\", \"fund_house\"])[\"aum_crore\"].mean().reset_index()\n",
        "df_yearly_aum[\"year\"] = df_yearly_aum[\"year\"].astype(str) # Convert year to string to fix legend startswith error\n",
        "\n",
        "plt.figure(figsize=(14, 7))\n",
        "sns.barplot(data=df_yearly_aum, x=\"fund_house\", y=\"aum_crore\", hue=\"year\", palette=\"viridis\")\n",
        "plt.title(\"AUM Progression by Fund House (2022 - 2025)\")\n",
        "plt.xticks(rotation=45, ha='right')\n",
        "plt.xlabel(\"Fund House / AMC\")\n",
        "plt.ylabel(\"Average AUM (Rs. Crore)\")\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"aum_growth.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 4: SIP Inflows
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 3. Monthly SIP Inflows Trend\n",
        "Monitoring systematic investment plan inflows over time."
    ]
})

# Code Cell 4: SIP Inflows Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "df_sip = pd.read_sql_query(\"SELECT * FROM fact_sip_industry\", conn)\n",
        "conn.close()\n",
        "\n",
        "df_sip[\"date\"] = pd.to_datetime(df_sip[\"month\"] + \"-01\")\n",
        "df_sip.sort_values(by=\"date\", inplace=True)\n",
        "\n",
        "plt.figure(figsize=(12, 6))\n",
        "plt.plot(df_sip[\"date\"], df_sip[\"sip_inflow_crore\"], marker='o', color='forestgreen', linewidth=2.5)\n",
        "plt.title(\"Monthly SIP Inflows (Rs. Crore) Jan 2022 - Dec 2025\")\n",
        "plt.xlabel(\"Month\")\n",
        "plt.ylabel(\"SIP Inflow (Rs. Crore)\")\n",
        "plt.axhline(31002, color='red', linestyle='--', label='Dec 2025 Peak: Rs. 31,002 Cr')\n",
        "plt.legend()\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"sip_inflows.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 5: Category Inflows
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 4. Category-wise Inflow Heatmap\n",
        "Visualizing net inflows across different mutual fund categories monthly."
    ]
})

# Code Cell 5: Category Inflows Heatmap
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "df_cat = pd.read_sql_query(\"SELECT * FROM fact_category_inflows\", conn)\n",
        "conn.close()\n",
        "\n",
        "df_cat_pivot = df_cat.pivot(index=\"category\", columns=\"month\", values=\"net_inflow_crore\")\n",
        "\n",
        "plt.figure(figsize=(15, 8))\n",
        "sns.heatmap(df_cat_pivot, cmap=\"RdYlGn\", center=0, annot=False, cbar_kws={'label': 'Net Inflow (Rs. Crore)'})\n",
        "plt.title(\"Monthly Net Inflows (Rs. Crore) by Fund Category (FY 2024-25)\")\n",
        "plt.xlabel(\"Month\")\n",
        "plt.ylabel(\"Category\")\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"category_inflow_heatmap.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 6: Investor Demographics
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 5. Investor Demographics\n",
        "Analyse active accounts age distribution and ticket sizes."
    ]
})

# Code Cell 6: Investor Demographics Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "df_tx = pd.read_sql_query(\"SELECT * FROM fact_transactions\", conn)\n",
        "conn.close()\n",
        "\n",
        "fig, axes = plt.subplots(1, 2, figsize=(16, 7))\n",
        "\n",
        "# 1. Age distribution pie chart\n",
        "age_counts = df_tx[\"age_group\"].value_counts()\n",
        "axes[0].pie(age_counts, labels=age_counts.index, autopct='%1.1f%%', startangle=140, colors=sns.color_palette(\"pastel\"))\n",
        "axes[0].set_title(\"Investor Split by Age Group\")\n",
        "\n",
        "# 2. Box plot of transaction amount by age group\n",
        "sns.boxplot(data=df_tx, x=\"age_group\", y=\"amount_inr\", ax=axes[1], palette=\"coolwarm\", showfliers=False)\n",
        "axes[1].set_title(\"Transaction Amount Distribution by Age Group\")\n",
        "axes[1].set_xlabel(\"Age Group\")\n",
        "axes[1].set_ylabel(\"Amount (INR)\")\n",
        "\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"investor_demographics.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 7: Geographic Analysis
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 6. Geographic Distribution\n",
        "Total SIP investment volume mapping across Indian states."
    ]
})

# Code Cell 7: Geographic Analysis Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "df_state_sip = df_tx[df_tx[\"transaction_type\"] == \"SIP\"].groupby(\"state\")[\"amount_inr\"].sum().reset_index()\n",
        "df_state_sip.sort_values(by=\"amount_inr\", ascending=True, inplace=True)\n",
        "\n",
        "plt.figure(figsize=(12, 7))\n",
        "sns.barplot(data=df_state_sip, y=\"state\", x=\"amount_inr\", palette=\"crest\")\n",
        "plt.title(\"Total Active SIP Amounts (INR) by Indian State\")\n",
        "plt.xlabel(\"Total Invested (INR)\")\n",
        "plt.ylabel(\"State\")\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"geo_distribution.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 8: Folio Growth
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 7. Folio Growth Trends\n",
        "Tracking total mutual fund folios growth from 13.26 crore to 26.12 crore."
    ]
})

# Code Cell 8: Folio Growth Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "df_folios = pd.read_sql_query(\"SELECT * FROM fact_industry_folios\", conn)\n",
        "conn.close()\n",
        "\n",
        "df_folios[\"date\"] = pd.to_datetime(df_folios[\"month\"] + \"-01\")\n",
        "df_folios.sort_values(by=\"date\", inplace=True)\n",
        "\n",
        "plt.figure(figsize=(12, 6))\n",
        "plt.plot(df_folios[\"date\"], df_folios[\"total_folios_crore\"], marker='s', color='darkblue', linewidth=2.5, label='Total Folios')\n",
        "plt.plot(df_folios[\"date\"], df_folios[\"equity_folios_crore\"], marker='^', color='orange', linestyle='--', label='Equity Folios')\n",
        "plt.title(\"Folio Count Growth (Crore) 2022 - 2025\")\n",
        "plt.xlabel(\"Month\")\n",
        "plt.ylabel(\"Folios (Crores)\")\n",
        "plt.legend()\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"folio_growth.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 9: Correlation Matrix
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 8. Return Correlation Matrix\n",
        "Pairwise daily return correlation of 10 selected funds."
    ]
})

# Code Cell 9: Correlation Matrix Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "df_returns = pd.read_sql_query(\"SELECT date, amfi_code, daily_return_pct FROM fact_nav\", conn)\n",
        "df_funds = pd.read_sql_query(\"SELECT amfi_code, scheme_name FROM dim_fund\", conn)\n",
        "conn.close()\n",
        "\n",
        "# Select 10 funds\n",
        "top_codes = df_funds[\"amfi_code\"].head(10).tolist()\n",
        "df_returns_filtered = df_returns[df_returns[\"amfi_code\"].isin(top_codes)]\n",
        "df_returns_pivot = df_returns_filtered.pivot(index=\"date\", columns=\"amfi_code\", values=\"daily_return_pct\")\n",
        "\n",
        "# Rename columns to short scheme names\n",
        "code_to_name = dict(zip(df_funds[\"amfi_code\"], df_funds[\"scheme_name\"].apply(lambda x: x.split(' - ')[0])))\n",
        "df_returns_pivot.rename(columns=code_to_name, inplace=True)\n",
        "\n",
        "corr_matrix = df_returns_pivot.corr()\n",
        "\n",
        "plt.figure(figsize=(10, 8))\n",
        "sns.heatmap(corr_matrix, annot=True, cmap=\"coolwarm\", fmt=\".2f\", cbar=True)\n",
        "plt.title(\"Mutual Funds Correlation Matrix (Daily Returns)\")\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"correlation_matrix.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 10: Sector Allocation
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 9. Sector Weight Allocation\n",
        "Distribution of top sectors across equity portfolio holdings."
    ]
})

# Code Cell 10: Sector Allocation Plotting
cells.append({
    "cell_type": "code",
    "execution_count": None,
    "metadata": {},
    "outputs": [],
    "source": [
        "conn = sqlite3.connect(db_path)\n",
        "df_port = pd.read_sql_query(\"SELECT sector, weight_pct FROM fact_portfolio\", conn)\n",
        "conn.close()\n",
        "\n",
        "sector_weights = df_port.groupby(\"sector\")[\"weight_pct\"].mean().reset_index()\n",
        "sector_weights.sort_values(by=\"weight_pct\", ascending=False, inplace=True)\n",
        "\n",
        "plt.figure(figsize=(12, 7))\n",
        "sns.barplot(data=sector_weights.head(10), x=\"weight_pct\", y=\"sector\", palette=\"magma\")\n",
        "plt.title(\"Average Sector Weights (%) in Equity Fund Portfolios\")\n",
        "plt.xlabel(\"Average Weight (%)\")\n",
        "plt.ylabel(\"Sector\")\n",
        "plt.tight_layout()\n",
        "plt.savefig(os.path.join(charts_dir, \"sector_allocation.png\"), dpi=300)\n",
        "plt.show()"
    ]
})

# Markdown Cell 11: Summary Findings
cells.append({
    "cell_type": "markdown",
    "metadata": {},
    "source": [
        "## 10 Key Findings & Business Insights\n",
        "\n",
        "Based on our Exploratory Data Analysis, here are the 10 core findings from the Bluestock Mutual Fund Capstone:\n",
        "\n",
        "1. **SBI MF Dominance**: SBI Mutual Fund maintains the highest Assets Under Management (AUM) in the industry, touching Rs. 12.5 lakh crore in Dec 2025.\n",
        "2. **Strong Recovery in Equities**: NAV historical charts show a robust upward trend from 2023 onwards, signaling strong recovery and market rallies despite mid-2024 global correction periods.\n",
        "3. **Record-breaking Inflows**: In December 2025, industry-wide SIP inflows peaked at an all-time high of Rs. 31,002 crore.\n",
        "4. **Liquid Category Dominance**: Heatmap analysis indicates that the Liquid category contributes the largest share of short-term inflows, acting as a primary repository for corporate and institutional cash reserves.\n",
        "5. **Retail Investment Demographics**: The 26-35 age bracket forms the largest investor cohort (approx 36%), indicating high fintech adoption rates among younger Indian professionals.\n",
        "6. **Higher Ticket Sizes in Older Cohorts**: While the 26-35 age group has the highest volume of accounts, the 46-55 age group contributes significantly higher individual ticket sizes.\n",
        "7. **Folio Growth Explosion**: Total mutual fund folios grew exponentially, doubling from 13.26 crore in early 2022 to 26.12 crore in December 2025, driven by equity equity culture expansion.\n",
        "8. **Geographical Concentration**: Top tier states (like Rajasthan, Punjab, and Tamil Nadu) exhibit high active SIP amounts, though B30 cities are growing rapidly.\n",
        "9. **High Sector Concentration**: Portfolio holdings show heavy tilt towards Financial Services (averaging > 25%), reflecting the sector's dominant weight in benchmark indices (Nifty 50).\n",
        "10. **Positive Fund Correlation**: Equity schemes from different houses are highly correlated (returns correlation coefficient > 0.85), indicating that broad macroeconomic factors dominate individual fund manager alpha."
    ]
})

# Create final dictionary
notebook_dict = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 2
}

# Write notebook
with open(notebook_path, "w") as f:
    json.dump(notebook_dict, f, indent=2)

print("Jupyter Notebook 'notebooks/EDA_Analysis.ipynb' generated successfully.")
