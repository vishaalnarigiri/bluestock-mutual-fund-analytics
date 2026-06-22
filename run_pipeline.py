import subprocess
import sys
import os

def run_script(script_name, cwd=None):
    script_path = os.path.join("scripts", script_name) if not cwd else script_name
    print("=" * 80)
    print(f"Running script: {script_name}...")
    print("=" * 80)
    
    result = subprocess.run([sys.executable, script_path], capture_output=False)
    if result.returncode != 0:
        print(f"Error: {script_name} failed with exit code {result.returncode}.")
        sys.exit(result.returncode)
    print(f"Completed {script_name} successfully.\n")

if __name__ == "__main__":
    print("=" * 80)
    print("BLUESTOCK MUTUAL FUND CAPSTONE: FULL DATA ENGINEERING & ETL PIPELINE")
    print("=" * 80)
    
    # 1. Clean data
    run_script("data_cleaning.py")
    
    # 2. Load database
    run_script("load_db.py")
    
    # 3. Calculate metrics and scorecard
    run_script("compute_metrics.py")
    
    # 4. Run advanced risk analytics
    run_script("advanced_analytics.py")
    
    # 5. Generate final PDF report
    run_script("generate_pdf_report.py")
    
    # 6. Generate final PPT presentation
    run_script("generate_presentation.py")
    
    print("=" * 80)
    print("ETL PIPELINE RUN COMPLETED SUCCESSFULLY!")
    print("All deliverables generated:")
    print(" - SQLite Database: db/bluestock_mf.db")
    print(" - Fund Scorecard: data/processed/fund_scorecard.csv")
    print(" - Advanced Reports: cohort_analysis.csv, sip_continuity.csv, sector_hhi.csv")
    print(" - PDF Report: reports/Project_Report.pdf")
    print(" - Presentation slides: reports/Presentation.pptx")
    print("=" * 80)
