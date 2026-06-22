import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import pandas as pd

pdf_path = "/Users/vaishnavnarigiri/Desktop/bluestock/reports/Project_Report.pdf"
charts_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/reports/charts"
processed_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/processed"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        if self._pageNumber == 1:
            return  # Suppress headers/footers on cover page
        
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#64748b"))
        
        # Header
        self.drawString(54, 750, "Bluestock Mutual Fund Analytics Platform — Capstone Report")
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Footer
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 40, page_text)
        self.drawString(54, 40, "CONFIDENTIAL — FOR INTERNAL USE ONLY")
        self.line(54, 52, 558, 52)
        self.restoreState()

def build_pdf():
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Styles matching premium brand
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=30,
        leading=36,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#475569"),
        spaceAfter=40
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#64748b")
    )
    
    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e3a8a"),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f766e"),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        leading=15,
        textColor=colors.HexColor("#334155"),
        spaceAfter=10
    )
    
    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#1e293b")
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    story = []
    
    # --- COVER PAGE ---
    story.append(Spacer(1, 150))
    story.append(Paragraph("MUTUAL FUND ANALYTICS PLATFORM", title_style))
    story.append(Paragraph("End-to-End Data Engineering, ETL Pipeline & Advanced Risk Analytics", subtitle_style))
    story.append(Spacer(1, 100))
    
    meta_text = """
    <b>Prepared For:</b> Bluestock Fintech Pvt. Ltd.<br/>
    <b>Domain:</b> Mutual Fund / Fintech Analytics<br/>
    <b>Project Type:</b> Capstone Project Submission<br/>
    <b>Prepared By:</b> Intern / Data Analyst<br/>
    <b>Date:</b> June 2026<br/>
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(PageBreak())
    
    # --- SECTION 1: INTRODUCTION & BUSINESS PROBLEM ---
    story.append(Paragraph("1. Executive Summary & Problem Statement", h1_style))
    story.append(Paragraph(
        "The Indian mutual fund industry has seen unprecedented growth, crossing Rs. 81 lakh crore in Assets Under Management (AUM) as of December 2025. "
        "However, individual investors, financial advisors, and distributors face massive hurdles in making optimal fund selections. This is driven by "
        "several key challenges in the current market landscape:",
        body_style
    ))
    
    problems = [
        "<b>P1: Data Fragmentation:</b> NAV history, quarterly AUM details, folio counts, and portfolio weights are spread across different sections of AMFI and private web sites in varying static forms (TXT, PDF, HTML).",
        "<b>P2: Performance Benchmarking Gaps:</b> Direct comparisons of funds across multiple Asset Management Companies (AMCs) on a risk-adjusted basis (Sharpe, Sortino, Alpha, Beta) require deep numeric calculations that are not readily available.",
        "<b>P3: Benchmark Outperformance Blind Spot:</b> Investors are frequently unaware if their fund is outperforming its benchmark, due to a lack of aligned index daily return metrics.",
        "<b>P4: Static Reporting Limits:</b> Asset management teams rely on static reporting spreadsheets that take days to prepare instead of modern, drill-down dashboards."
    ]
    for p in problems:
        story.append(Paragraph(f"• {p}", body_style))
    story.append(Spacer(1, 10))
    
    # --- SECTION 2: SYSTEM ARCHITECTURE & ETL ---
    story.append(Paragraph("2. System Architecture & ETL Pipeline", h1_style))
    story.append(Paragraph(
        "To solve these challenges, we built a classic Fintech Data Platform architecture following the extract-transform-load (ETL) pipeline pattern. "
        "The system connects to live financial REST APIs, consolidates disjointed datasets, structures a relational database, and exposes insights via a web application.",
        body_style
    ))
    
    # Data Ingestion details
    story.append(Paragraph("2.1 Data Ingestion Phase", h2_style))
    story.append(Paragraph(
        "10 distinct CSV datasets from AMFI and other historical public records were loaded, parsed, and checked. "
        "Additionally, a REST API fetcher script (<code>live_nav_fetch.py</code>) was written to scrape live NAV histories from the public "
        "mutual fund API (<code>mfapi.in</code>) for HDFC Top 100, SBI Bluechip, ICICI Bluechip, Nippon Large Cap, Axis Bluechip, and Kotak Bluechip. "
        "This data was saved as flat files to anchor the historical calculations with live market updates.",
        body_style
    ))
    
    # Database Design details
    story.append(Paragraph("2.2 Normalized Star Schema Design", h2_style))
    story.append(Paragraph(
        "We designed and initialized a normalized Star Schema in SQLite (<code>bluestock_mf.db</code>) to optimize query performance. "
        "The tables consist of: <code>dim_fund</code> (fund house and category metadata), <code>dim_date</code> (date lookup calendar containing month, year, and weekday identifiers), "
        "<code>fact_nav</code> (daily NAV records), <code>fact_transactions</code> (investor transactions log), <code>fact_performance</code> (calculated risk metrics), "
        "and <code>fact_portfolio</code> (fund stock holdings).",
        body_style
    ))
    
    # Schema table
    schema_data = [
        [Paragraph("Table Name", table_header_style), Paragraph("Type", table_header_style), Paragraph("Key Fields", table_header_style), Paragraph("Purpose", table_header_style)],
        [Paragraph("dim_fund", table_cell_style), Paragraph("Dimension", table_cell_style), Paragraph("amfi_code (PK)", table_cell_style), Paragraph("Scheme details, AMC names, SEBI categories", table_cell_style)],
        [Paragraph("dim_date", table_cell_style), Paragraph("Dimension", table_cell_style), Paragraph("date (PK)", table_cell_style), Paragraph("Calendar lookup with quarter, weekday indicator", table_cell_style)],
        [Paragraph("fact_nav", table_cell_style), Paragraph("Fact", table_cell_style), Paragraph("amfi_code, date (PK)", table_cell_style), Paragraph("Daily NAV historical series and computed return %", table_cell_style)],
        [Paragraph("fact_transactions", table_cell_style), Paragraph("Fact", table_cell_style), Paragraph("tx_id (PK), investor_id", table_cell_style), Paragraph("Log of simulated retail transactions, states, and KYC", table_cell_style)],
        [Paragraph("fact_performance", table_cell_style), Paragraph("Fact", table_cell_style), Paragraph("amfi_code (PK)", table_cell_style), Paragraph("CAGRs, Sharpe, Sortino, Alpha, Beta, VaR", table_cell_style)]
    ]
    t = Table(schema_data, colWidths=[1.1*inch, 0.9*inch, 1.5*inch, 2.5*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1e3a8a")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
    ]))
    story.append(t)
    story.append(PageBreak())
    
    # --- SECTION 3: EDA ---
    story.append(Paragraph("3. Exploratory Data Analysis (EDA)", h1_style))
    story.append(Paragraph(
        "A deep Exploratory Data Analysis was carried out using Matplotlib and Seaborn. Charts were generated to understand market behavior, "
        "AUM distributions, investor demographics, and systemic transaction patterns.",
        body_style
    ))
    
    # Insert charts with text descriptions
    charts = [
        ("nav_trends.png", "Figure 3.1: NAV Historical trends for large cap schemes showing clear post-2023 rallies."),
        ("aum_growth.png", "Figure 3.2: Assets Under Management growth by AMC, highlighting SBI MF's dominant position."),
        ("sip_inflows.png", "Figure 3.3: Systematic Investment Inflows demonstrating the record ₹31,002 Cr in Dec 2025."),
        ("category_inflow_heatmap.png", "Figure 3.4: Category Inflows intensity heatmap across Large Cap, Small Cap, and Liquid funds.")
    ]
    
    for filename, caption in charts:
        img_path = os.path.join(charts_dir, filename)
        if os.path.exists(img_path):
            story.append(Image(img_path, width=5.5*inch, height=2.8*inch))
            story.append(Paragraph(f"<i>{caption}</i>", ParagraphStyle('Caption', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#475569"), alignment=1)))
            story.append(Spacer(1, 15))
            
    story.append(PageBreak())
    
    # Part 2 of EDA charts
    more_charts = [
        ("investor_demographics.png", "Figure 3.5: Investor demographics split by age brackets and transaction amount boxes."),
        ("geo_distribution.png", "Figure 3.6: Geographic distribution of total SIP investment amounts across Indian states."),
        ("folio_growth.png", "Figure 3.7: Rapid expansion of mutual fund folios driven by equity products."),
        ("correlation_matrix.png", "Figure 3.8: High returns correlation coefficient (> 0.85) between major large-cap schemes.")
    ]
    for filename, caption in more_charts:
        img_path = os.path.join(charts_dir, filename)
        if os.path.exists(img_path):
            story.append(Image(img_path, width=5.5*inch, height=2.8*inch))
            story.append(Paragraph(f"<i>{caption}</i>", ParagraphStyle('Caption2', parent=styles['Normal'], fontSize=8.5, textColor=colors.HexColor("#475569"), alignment=1)))
            story.append(Spacer(1, 15))
            
    story.append(PageBreak())
    
    # --- SECTION 4: PERFORMANCE & SCORECARD ---
    story.append(Paragraph("4. Performance Analytics & Fund Scorecard", h1_style))
    story.append(Paragraph(
        "Using the daily NAV histories and corresponding benchmark index prices, we computed the CAGR, risk-adjusted performance indicators "
        "(Sharpe & Sortino), portfolio beta (regression slope vs. Nifty 100), and portfolio alpha. A ranking model was built to score funds "
        "on a 0-100 scale, with the top performing funds highlighted below.",
        body_style
    ))
    
    # Scorecard Table
    scorecard_file = os.path.join(processed_dir, "fund_scorecard.csv")
    if os.path.exists(scorecard_file):
        df_score = pd.read_csv(scorecard_file).head(8)
        score_data = [
            [Paragraph("Scheme Name", table_header_style), Paragraph("AMC", table_header_style), Paragraph("3yr CAGR", table_header_style), Paragraph("Sharpe", table_header_style), Paragraph("Alpha %", table_header_style), Paragraph("Drawdown", table_header_style), Paragraph("Score", table_header_style)]
        ]
        for _, r in df_score.iterrows():
            score_data.append([
                Paragraph(r["scheme_name"].split(" - ")[0], table_cell_style),
                Paragraph(r["fund_house"].split(" ")[0], table_cell_style),
                Paragraph(f"{r['return_3yr_pct']:.2f}%", table_cell_style),
                Paragraph(f"{r['sharpe_ratio']:.2f}", table_cell_style),
                Paragraph(f"{r['alpha']:.2f}%", table_cell_style),
                Paragraph(f"{r['max_drawdown_pct']:.2f}%", table_cell_style),
                Paragraph(f"{r['composite_score']:.1f}", table_cell_style)
            ])
        t_score = Table(score_data, colWidths=[1.8*inch, 1.0*inch, 0.8*inch, 0.7*inch, 0.8*inch, 0.9*inch, 0.6*inch])
        t_score.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#0f766e")),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f8fafc")]),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('BOTTOMPADDING', (0,0), (-1,0), 5),
            ('TOPPADDING', (0,0), (-1,0), 5),
        ]))
        story.append(t_score)
        
    story.append(Spacer(1, 15))
    story.append(Paragraph("4.1 Risk and Downside Highlights", h2_style))
    story.append(Paragraph(
        "• <b>Alpha Performance:</b> Mirae Asset Large Cap Fund leads the group with an annualized alpha of 26.96% above Nifty 100.<br/>"
        "• <b>Downside Volatility:</b> Mid-cap and small-cap funds demonstrated higher Sortino ratios but suffered drawdowns exceeding 18% during corrections, "
        "reinforcing the need for long-term holding strategies.",
        body_style
    ))
    
    # --- SECTION 5: ADVANCED ANALYTICS ---
    story.append(Paragraph("5. Advanced Risk Analytics & Investor Churn", h1_style))
    story.append(Paragraph(
        "To provide institution-level financial intelligence, we deployed three advanced modules: Cohort Analysis, Value at Risk (VaR), and Churn Prediction.",
        body_style
    ))
    
    story.append(Paragraph("5.1 Value at Risk (VaR) & CVaR", h2_style))
    story.append(Paragraph(
        "We computed daily Historical VaR (95% confidence) and Conditional VaR (CVaR). VaR represents the worst-case expected loss on a single day, "
        "while CVaR measures the average loss in the worst 5% of trading sessions. For example, large-cap equity funds exhibit a daily VaR of "
        "around -1.25%, whereas small-cap schemes exhibit a VaR exceeding -1.80%.",
        body_style
    ))
    
    story.append(Paragraph("5.2 Investor Cohort Analysis", h2_style))
    story.append(Paragraph(
        "We segmented investors based on their first transaction year (2024 vs 2025 cohorts) and compared behaviors. "
        "The 2024 investor cohort has a higher cumulative transaction count, while the 2025 cohort demonstrates higher average "
        "monthly SIP ticket sizes, reflecting inflation and retail participation growth.",
        body_style
    ))
    
    story.append(Paragraph("5.3 SIP Churn Prediction (Continuity)", h2_style))
    story.append(Paragraph(
        "We implemented a systematic continuity tracker that monitors the elapsed days between consecutive SIP transactions for investors with "
        "at least 6 active cycles. Investors with transaction gaps exceeding 35 days were flagged as 'at-risk' of churning or canceling their SIP plans. "
        "This is an early warning system for AMC distribution teams.",
        body_style
    ))
    
    story.append(PageBreak())
    
    # --- SECTION 6: CONCLUSION & BUSINESS RECOMMENDATIONS ---
    story.append(Paragraph("6. Business Recommendations & Conclusions", h1_style))
    story.append(Paragraph(
        "1. <b>Targeted Campaign for At-Risk SIPs:</b> AMC marketing teams should leverage the churn warning flags to trigger automated UPI mandate reminders "
        "for investors whose transaction gap approaches 30 days, preventing drop-offs.",
        body_style
    ))
    story.append(Paragraph(
        "2. <b>Expand B30 Geographical Outlets:</b> Retail transaction volumes indicate a high concentration in primary states (Punjab, TN, Rajasthan). "
        "Deploying distributor hubs in Beyond-30 (B30) tier cities presents massive untapped growth vectors.",
        body_style
    ))
    story.append(Paragraph(
        "3. <b>Promote Low-Expense Direct Funds:</b> Slicing funds by expense ratios shows a clear cost advantage for direct schemes. Advisories should highlight "
        "these products to self-service retail cohorts to drive platform loyalty.",
        body_style
    ))
    story.append(Paragraph(
        "4. <b>Dynamic Risk Profiling:</b> Integrate the custom <code>recommender.py</code> logic directly into client portals, matching low-risk, moderate-risk, "
        "and high-risk appetites to objective Sharpe rankings.",
        body_style
    ))
    
    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print("Project PDF Report generated successfully.")

if __name__ == "__main__":
    build_pdf()
