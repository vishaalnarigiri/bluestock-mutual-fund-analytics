import os
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Set page config
st.set_page_config(
    page_title="Bluestock Mutual Fund Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Design
st.markdown("""
<style>
    /* Main body background and fonts */
    .main {
        background-color: #f7f9fc;
        font-family: 'Outfit', sans-serif;
    }
    
    /* Header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.5rem;
        border-bottom: 3px solid #3b82f6;
        padding-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #64748b;
        margin-bottom: 2rem;
    }
    
    /* KPI Card styling */
    .kpi-container {
        display: flex;
        gap: 1.5rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -1px rgba(0,0,0,0.06);
        padding: 1.5rem;
        flex: 1;
        border-left: 5px solid #3b82f6;
        transition: transform 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #64748b;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.05em;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0.3rem 0;
    }
    
    .kpi-subtext {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Database path
db_path = "/Users/vaishnavnarigiri/Desktop/bluestock/db/bluestock_mf.db"

# Data Helpers
def get_connection():
    return sqlite3.connect(db_path)

@st.cache_data
def load_dim_funds():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM dim_fund", conn)
    conn.close()
    return df

@st.cache_data
def load_performance_data():
    conn = get_connection()
    df = pd.read_sql_query("""
        SELECT f.*, p.return_1yr_pct, p.return_3yr_pct, p.return_5yr_pct, 
               p.alpha, p.beta, p.sharpe_ratio, p.sortino_ratio, p.std_dev_ann_pct,
               p.max_drawdown_pct, p.morningstar_rating, p.composite_score
        FROM dim_fund f
        JOIN fact_performance p ON f.amfi_code = p.amfi_code
    """, conn)
    conn.close()
    return df

# Initialize Sidebar Filters
st.sidebar.image("https://bluestock.in/assets/img/logo.png", width=180)
st.sidebar.markdown("---")
st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to Page", ["Industry Overview", "Fund Performance", "Investor Analytics", "SIP & Market Trends"])

st.sidebar.markdown("---")
st.sidebar.header("Global Filters")

df_funds_all = load_dim_funds()
amcs = sorted(df_funds_all["fund_house"].unique())
categories = sorted(df_funds_all["category"].unique())
risk_grades = sorted(df_funds_all["risk_category"].unique())

selected_amc = st.sidebar.multiselect("Select Asset Management Company (AMC)", amcs, default=[])
selected_cat = st.sidebar.multiselect("Select Fund Category", categories, default=[])
selected_risk = st.sidebar.multiselect("Select Risk Level", risk_grades, default=[])

# Apply filters helper
def filter_df(df):
    filtered_df = df.copy()
    if selected_amc:
        filtered_df = filtered_df[filtered_df["fund_house"].isin(selected_amc)]
    if selected_cat:
        filtered_df = filtered_df[filtered_df["category"].isin(selected_cat)]
    if selected_risk:
        filtered_df = filtered_df[filtered_df["risk_category"].isin(selected_risk)]
    return filtered_df

# Title block
st.markdown('<div class="main-header">Bluestock Mutual Fund Analytics Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Premium End-to-End Fintech ETL & Insights Dashboard</div>', unsafe_allow_html=True)

# ----------------- PAGE 1: Industry Overview -----------------
if page == "Industry Overview":
    st.header("Industry Overview & AMC Landscape")
    
    # Custom KPI Cards using HTML/CSS
    st.markdown("""
    <div style="display: flex; gap: 1.5rem; margin-bottom: 2rem;">
        <div class="kpi-card" style="border-left: 5px solid #3b82f6;">
            <div class="kpi-label">Total Industry AUM</div>
            <div class="kpi-value">₹81.0 L Cr</div>
            <div class="kpi-subtext">Peak Dec 2025 Milestone</div>
        </div>
        <div class="kpi-card" style="border-left: 5px solid #10b981;">
            <div class="kpi-label">Active SIP Inflow</div>
            <div class="kpi-value">₹31,002 Cr</div>
            <div class="kpi-subtext">↗ +20.3% YoY Growth</div>
        </div>
        <div class="kpi-card" style="border-left: 5px solid #f59e0b;">
            <div class="kpi-label">Total Folio Count</div>
            <div class="kpi-value">26.12 Cr</div>
            <div class="kpi-subtext">↗ Equity Led Expansion</div>
        </div>
        <div class="kpi-card" style="border-left: 5px solid #8b5cf6;">
            <div class="kpi-label">Tracked Schemes</div>
            <div class="kpi-value">40 / 1,908</div>
            <div class="kpi-subtext">Key Schemes Ingested</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    conn = get_connection()
    df_aum = pd.read_sql_query("SELECT * FROM fact_aum", conn)
    df_sip_ind = pd.read_sql_query("SELECT * FROM fact_sip_industry", conn)
    conn.close()
    
    df_aum["date"] = pd.to_datetime(df_aum["date"])
    df_sip_ind["date"] = pd.to_datetime(df_sip_ind["month"] + "-01")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Industry AUM Growth Trend (2022 - 2025)")
        # Aggregate monthly/quarterly industry average AUM
        df_aum_agg = df_aum.groupby("date")["aum_crore"].sum().reset_index()
        # Scale to Lakh Crore
        df_aum_agg["aum_lakh_crore"] = df_aum_agg["aum_crore"] / 100000.0
        fig_aum = px.line(df_aum_agg, x="date", y="aum_lakh_crore", markers=True,
                          labels={"aum_lakh_crore": "Industry AUM (Rs. Lakh Crore)", "date": "Date"},
                          color_discrete_sequence=["#3b82f6"])
        fig_aum.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=380)
        st.plotly_chart(fig_aum, use_container_width=True)
        
    with col2:
        st.subheader("Top 10 Fund Houses by Average AUM")
        df_amc_aum = df_aum[df_aum["date"] == df_aum["date"].max()].sort_values(by="aum_crore", ascending=False)
        fig_amc = px.bar(df_amc_aum, x="fund_house", y="aum_crore", 
                         labels={"aum_crore": "AUM (Rs. Crore)", "fund_house": "AMC"},
                         color="aum_crore", color_continuous_scale="Blues")
        fig_amc.update_layout(margin=dict(l=20, r=20, t=30, b=20), height=380, showlegend=False)
        st.plotly_chart(fig_amc, use_container_width=True)

# ----------------- PAGE 2: Fund Performance -----------------
elif page == "Fund Performance":
    st.header("Fund Risk-Return Performance Analytics")
    
    df_perf = load_performance_data()
    df_perf_filtered = filter_df(df_perf)
    
    # Performance cards
    top_fund_row = df_perf_filtered.sort_values(by="composite_score", ascending=False).iloc[0] if not df_perf_filtered.empty else None
    
    col1, col2, col3 = st.columns(3)
    if top_fund_row is not None:
        with col1:
            st.metric("Top Ranked Fund (by Composite Score)", top_fund_row["scheme_name"].split(" - ")[0], 
                      f"Score: {top_fund_row['composite_score']:.1f}")
        with col2:
            st.metric("Average 3yr CAGR Return", f"{df_perf_filtered['return_3yr_pct'].mean():.2f}%")
        with col3:
            st.metric("Average Sharpe Ratio", f"{df_perf_filtered['sharpe_ratio'].mean():.2f}")
            
    st.markdown("---")
    
    col_g1, col_g2 = st.columns([3, 2])
    
    with col_g1:
        st.subheader("Risk vs. Return Mapping (Bubble size = AUM)")
        # Scatter return (3yr CAGR) vs Risk (Std Dev)
        fig_scatter = px.scatter(
            df_perf_filtered, 
            x="std_dev_ann_pct", 
            y="return_3yr_pct",
            size="aum_crore", 
            color="risk_category",
            hover_name="scheme_name", 
            labels={"std_dev_ann_pct": "Annualised Volatility / Risk (%)", "return_3yr_pct": "3yr CAGR Return (%)"},
            color_discrete_map={"Low": "green", "Moderate": "blue", "Moderately High": "orange", "High": "red", "Very High": "darkred"},
            height=450
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col_g2:
        st.subheader("Selected Fund NAV vs. Benchmark closing value")
        # Select single fund to view NAV comparison
        fund_list = sorted(df_perf_filtered["scheme_name"].tolist())
        selected_fund = st.selectbox("Select Scheme to benchmark", fund_list) if fund_list else None
        
        if selected_fund:
            selected_amfi = df_perf_filtered[df_perf_filtered["scheme_name"] == selected_fund].iloc[0]["amfi_code"]
            selected_bench_name = df_perf_filtered[df_perf_filtered["scheme_name"] == selected_fund].iloc[0]["benchmark"]
            
            conn = get_connection()
            # Fetch NAV history
            df_fn = pd.read_sql_query(f"SELECT date, nav FROM fact_nav WHERE amfi_code = {selected_amfi}", conn)
            # Fetch benchmark indices
            mapped_bench = benchmark_mapping.get(selected_bench_name, "NIFTY100")
            df_bn = pd.read_sql_query(f"SELECT date, close_value FROM clean_benchmark_indices WHERE index_name = '{mapped_bench}'", conn)
            conn.close()
            
            df_fn["date"] = pd.to_datetime(df_fn["date"])
            df_bn["date"] = pd.to_datetime(df_bn["date"])
            
            # Merge and normalize to 100 for comparison
            df_merged = pd.merge(df_fn, df_bn, on="date").sort_values("date")
            if not df_merged.empty:
                df_merged["normalized_nav"] = (df_merged["nav"] / df_merged["nav"].iloc[0]) * 100.0
                df_merged["normalized_bench"] = (df_merged["close_value"] / df_merged["close_value"].iloc[0]) * 100.0
                
                fig_compare = go.Figure()
                fig_compare.add_trace(go.Scatter(x=df_merged["date"], y=df_merged["normalized_nav"], name="Fund NAV (Normalized)", line=dict(color="#3b82f6", width=2)))
                fig_compare.add_trace(go.Scatter(x=df_merged["date"], y=df_merged["normalized_bench"], name=f"Benchmark: {mapped_bench} (Normalized)", line=dict(color="#64748b", width=2, dash='dash')))
                fig_compare.update_layout(height=360, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_compare, use_container_width=True)
                
    st.subheader("Sortable Fund Performance Scorecard")
    st.dataframe(
        df_perf_filtered[[
            "scheme_name", "fund_house", "category", "risk_category", "expense_ratio_pct",
            "return_1yr_pct", "return_3yr_pct", "return_5yr_pct", "sharpe_ratio", "sortino_ratio", "alpha", "beta", "max_drawdown_pct", "composite_score"
        ]].sort_values("composite_score", ascending=False).style.format({
            "expense_ratio_pct": "{:.2f}%",
            "return_1yr_pct": "{:.2f}%",
            "return_3yr_pct": "{:.2f}%",
            "return_5yr_pct": "{:.2f}%",
            "sharpe_ratio": "{:.2f}",
            "sortino_ratio": "{:.2f}",
            "alpha": "{:.2f}",
            "beta": "{:.2f}",
            "max_drawdown_pct": "{:.2f}%",
            "composite_score": "{:.1f}"
        }),
        use_container_width=True
    )

# ----------------- PAGE 3: Investor Analytics -----------------
elif page == "Investor Analytics":
    st.header("Investor Behaviour & Demographic Segmentation")
    
    conn = get_connection()
    df_tx = pd.read_sql_query("SELECT * FROM fact_transactions", conn)
    conn.close()
    
    # Filter transaction dataset based on sidebar fund selection
    # Gather amfi codes matching global filters
    df_perf = load_performance_data()
    df_perf_filtered = filter_df(df_perf)
    valid_amfi = set(df_perf_filtered["amfi_code"])
    
    df_tx_filtered = df_tx[df_tx["amfi_code"].isin(valid_amfi)].copy()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("Geographical Distribution (State-wise Volume)")
        state_vol = df_tx_filtered.groupby("state")["amount_inr"].sum().reset_index()
        state_vol = state_vol.sort_values(by="amount_inr", ascending=False)
        fig_state = px.bar(state_vol, x="state", y="amount_inr", color="amount_inr", color_continuous_scale="Tealgrn")
        fig_state.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=350, showlegend=False)
        st.plotly_chart(fig_state, use_container_width=True)
        
    with col2:
        st.subheader("Transaction Type Breakdown")
        tx_split = df_tx_filtered.groupby("transaction_type")["amount_inr"].sum().reset_index()
        fig_donut = px.pie(tx_split, values="amount_inr", names="transaction_type", hole=0.4,
                           color_discrete_sequence=px.colors.qualitative.Pastel)
        fig_donut.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=350)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col3:
        st.subheader("Average Investment by Age Group")
        age_avg = df_tx_filtered.groupby("age_group")["amount_inr"].mean().reset_index()
        fig_age = px.bar(age_avg, x="age_group", y="amount_inr", color="age_group",
                         color_discrete_sequence=px.colors.categorical.G10)
        fig_age.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=350, showlegend=False)
        st.plotly_chart(fig_age, use_container_width=True)

# ----------------- PAGE 4: SIP & Market Trends -----------------
elif page == "SIP & Market Trends":
    st.header("Industry SIP Inflows vs Market Benchmarks")
    
    conn = get_connection()
    df_sip = pd.read_sql_query("SELECT * FROM fact_sip_industry", conn)
    df_bench = pd.read_sql_query("SELECT * FROM clean_benchmark_indices WHERE index_name = 'NIFTY50'", conn)
    df_cat = pd.read_sql_query("SELECT * FROM fact_category_inflows", conn)
    conn.close()
    
    df_sip["date"] = pd.to_datetime(df_sip["month"] + "-01")
    df_bench["date"] = pd.to_datetime(df_bench["date"])
    
    # Align dates for dual axis
    df_bench_monthly = df_bench.groupby(df_bench["date"].dt.to_period('M'))["close_value"].last().reset_index()
    df_bench_monthly["date"] = pd.to_datetime(df_bench_monthly["date"].dt.to_timestamp())
    
    df_aligned = pd.merge(df_sip, df_bench_monthly, on="date").sort_values("date")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.subheader("Monthly SIP Inflow (Rs. Crore) vs. Nifty 50 Index")
        # Dual axis using Plotly graph objects
        fig_dual = go.Figure()
        
        # Bars for SIP Inflow
        fig_dual.add_trace(go.Bar(
            x=df_aligned["date"],
            y=df_aligned["sip_inflow_crore"],
            name="SIP Inflow (Rs. Cr)",
            marker_color="#a7f3d0",
            yaxis="y"
        ))
        
        # Line for Nifty 50
        fig_dual.add_trace(go.Scatter(
            x=df_aligned["date"],
            y=df_aligned["close_value"],
            name="Nifty 50 Close",
            line=dict(color="#2563eb", width=3),
            yaxis="y2"
        ))
        
        # Configure layout for dual axis
        fig_dual.update_layout(
            yaxis=dict(title="SIP Inflow (Rs. Crore)", titlefont=dict(color="#10b981"), tickfont=dict(color="#10b981")),
            yaxis2=dict(title="Nifty 50 Index Value", titlefont=dict(color="#2563eb"), tickfont=dict(color="#2563eb"), overlaying="y", side="right"),
            legend=dict(x=0.05, y=0.95),
            margin=dict(l=20, r=20, t=30, b=20),
            height=400
        )
        st.plotly_chart(fig_dual, use_container_width=True)
        
    with col2:
        st.subheader("Category-wise net inflows heatmap")
        df_cat_pivot = df_cat.pivot(index="category", columns="month", values="net_inflow_crore")
        fig_heatmap = px.imshow(
            df_cat_pivot, 
            labels=dict(x="Month", y="Category", color="Net Inflow (Cr)"),
            color_continuous_scale="RdYlGn"
        )
        fig_heatmap.update_layout(margin=dict(l=10, r=10, t=10, b=10), height=400)
        st.plotly_chart(fig_heatmap, use_container_width=True)
