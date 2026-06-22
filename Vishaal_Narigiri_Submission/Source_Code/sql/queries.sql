-- Bluestock Mutual Fund Analytics SQL Queries
-- Answering business questions for the Fintech Analytics platform

-- 1. Top 5 Funds by AUM
-- Retreives the 5 largest funds in the portfolio by Assets Under Management (AUM)
SELECT amfi_code, scheme_name, aum_crore, morningstar_rating
FROM fact_performance
ORDER BY aum_crore DESC
LIMIT 5;


-- 2. Monthly Average NAV for SBI Bluechip (AMFI: 119551)
-- Calculates the average NAV of the SBI Bluechip Fund grouped by calendar month
SELECT SUBSTR(date, 1, 7) AS month, 
       AVG(nav) AS average_nav,
       MIN(nav) AS min_nav,
       MAX(nav) AS max_nav
FROM fact_nav
WHERE amfi_code = 119551
GROUP BY month
ORDER BY month;


-- 3. SIP Inflow YoY Growth Analysis
-- Uses SQL window functions (LAG) to compute the Year-over-Year (YoY) SIP inflow growth rates
SELECT month,
       sip_inflow_crore,
       LAG(sip_inflow_crore, 12) OVER (ORDER BY month) AS prev_year_sip_inflow_crore,
       ROUND(((sip_inflow_crore - LAG(sip_inflow_crore, 12) OVER (ORDER BY month)) * 100.0) / 
             LAG(sip_inflow_crore, 12) OVER (ORDER BY month), 2) AS calculated_yoy_growth_pct,
       yoy_growth_pct AS recorded_yoy_growth_pct
FROM fact_sip_industry
ORDER BY month
LIMIT 12 OFFSET 12; -- Shows comparisons after a full year of history has passed


-- 4. Investor Transactions volume and value by Indian State
-- Summarizes investment volume, total transactions value, and average investment ticket size per state
SELECT state,
       COUNT(*) AS transaction_count,
       SUM(amount_inr) AS total_invested_inr,
       ROUND(AVG(amount_inr), 2) AS avg_ticket_size_inr
FROM fact_transactions
GROUP BY state
ORDER BY total_invested_inr DESC;


-- 5. Low Expense Ratio Funds (expense_ratio < 1.0%)
-- Identifies passive or direct fund schemes with low management charges
SELECT amfi_code, scheme_name, expense_ratio_pct, fund_house
FROM dim_fund
WHERE expense_ratio_pct < 1.0
ORDER BY expense_ratio_pct ASC;


-- 6. Category-wise net inflow for FY 2024-25
-- Sums up category inflows during the Indian financial year 2024-2025
SELECT category,
       SUM(net_inflow_crore) AS total_net_inflow_crore
FROM fact_category_inflows
WHERE month >= '2024-04' AND month <= '2025-03'
GROUP BY category
ORDER BY total_net_inflow_crore DESC;


-- 7. Number of Transaction Payments by Payment Mode
-- Understands popular payment channels preferred by retail investors
SELECT payment_mode,
       COUNT(*) AS tx_count,
       SUM(amount_inr) AS total_amount_inr
FROM fact_transactions
GROUP BY payment_mode
ORDER BY tx_count DESC;


-- 8. Count of KYC Verified vs Pending Investors
-- Identifies compliance volumes and risks
SELECT kyc_status,
       COUNT(DISTINCT investor_id) AS unique_investors,
       COUNT(*) AS transaction_count
FROM fact_transactions
GROUP BY kyc_status;


-- 9. Top 5 States by Active SIP Volume
-- Identifies states contributing most to systematic monthly recurring investment inflows
SELECT state,
       SUM(amount_inr) AS total_sip_amount_inr,
       COUNT(*) AS sip_count
FROM fact_transactions
WHERE transaction_type = 'SIP'
GROUP BY state
ORDER BY total_sip_amount_inr DESC
LIMIT 5;


-- 10. Direct and Regular schemes with 0% exit load
-- Identifies mutual funds that permit early redemptions without exit penalties
SELECT amfi_code, scheme_name, exit_load_pct, category, risk_category
FROM dim_fund
WHERE exit_load_pct = 0.0
ORDER BY scheme_name;
