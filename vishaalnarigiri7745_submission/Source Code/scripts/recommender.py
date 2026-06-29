import os
import sqlite3
import pandas as pd
import sys

db_path = "/Users/vaishnavnarigiri/Desktop/bluestock/db/bluestock_mf.db"

# Risk appetite mapping to DB risk categories
risk_map = {
    "low": ["Low", "Moderate"],
    "moderate": ["Moderately High"],
    "high": ["High", "Very High"]
}

def get_recommendations(risk_appetite):
    risk_appetite = risk_appetite.lower().strip()
    if risk_appetite not in risk_map:
        raise ValueError("Invalid risk appetite. Choose from: Low, Moderate, High")
        
    db_risk_categories = risk_map[risk_appetite]
    
    # Query database
    conn = sqlite3.connect(db_path)
    # Parametrized query to avoid SQL injection
    placeholders = ",".join("?" for _ in db_risk_categories)
    query = f"""
        SELECT f.amfi_code, f.scheme_name, f.fund_house, f.category, f.risk_category, f.expense_ratio_pct,
               p.return_3yr_pct, p.sharpe_ratio, p.composite_score
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
        WHERE f.risk_category IN ({placeholders})
        ORDER BY p.sharpe_ratio DESC
        LIMIT 3
    """
    df = pd.read_sql_query(query, conn, params=db_risk_categories)
    conn.close()
    return df

if __name__ == "__main__":
    # Command line interface
    if len(sys.argv) > 1:
        risk = sys.argv[1]
    else:
        risk = "Low"
        
    print(f"Generating Top 3 Mutual Fund recommendations for Risk Appetite: '{risk}'...")
    try:
        recommendations = get_recommendations(risk)
        if recommendations.empty:
            print("No matching funds found in the database.")
        else:
            print(recommendations.to_markdown(index=False))
    except Exception as e:
        print(f"Error: {e}")
