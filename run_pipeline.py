import subprocess
import sys
import os
import shutil

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

def sync_submission_folder():
    print("=" * 80)
    print("Syncing updated files to vishaalnarigiri7745_submission folder...")
    print("=" * 80)
    
    sub_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/vishaalnarigiri7745_submission"
    
    # 1. Sync Cleaned Datasets
    dest_clean_data = os.path.join(sub_dir, "Datasets", "Cleaned_Data")
    os.makedirs(dest_clean_data, exist_ok=True)
    for item in os.listdir("data/processed"):
        src_path = os.path.join("data/processed", item)
        if os.path.isfile(src_path):
            shutil.copy2(src_path, dest_clean_data)
            
    # 2. Sync Documentation
    dest_doc = os.path.join(sub_dir, "Documentation")
    os.makedirs(dest_doc, exist_ok=True)
    if os.path.exists("reports/Project_Report.pdf"):
        shutil.copy2("reports/Project_Report.pdf", dest_doc)
    if os.path.exists("reports/Dashboard.pdf"):
        shutil.copy2("reports/Dashboard.pdf", dest_doc)
    if os.path.exists("reports/data_quality_summary.md"):
        shutil.copy2("reports/data_quality_summary.md", dest_doc)
    if os.path.exists("data_dictionary.md"):
        shutil.copy2("data_dictionary.md", dest_doc)
        
    # 2b. Sync PDF folder (in root and submission)
    root_pdf_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/pdf"
    sub_pdf_dir = os.path.join(sub_dir, "pdf")
    os.makedirs(root_pdf_dir, exist_ok=True)
    os.makedirs(sub_pdf_dir, exist_ok=True)
    for pdf_file in ["Project_Report.pdf", "Dashboard.pdf"]:
        src_pdf = os.path.join("reports", pdf_file)
        if os.path.exists(src_pdf):
            shutil.copy2(src_pdf, root_pdf_dir)
            shutil.copy2(src_pdf, sub_pdf_dir)

        
    # 3. Sync PowerPoint
    dest_ppt = os.path.join(sub_dir, "PPT_Slides")
    os.makedirs(dest_ppt, exist_ok=True)
    if os.path.exists("reports/Presentation.pptx"):
        shutil.copy2("reports/Presentation.pptx", dest_ppt)
        
    # 4. Sync Source Code
    dest_src = os.path.join(sub_dir, "Source_Code")
    # Clean and sync dashboard
    if os.path.exists(os.path.join(dest_src, "dashboard")):
        shutil.rmtree(os.path.join(dest_src, "dashboard"))
    shutil.copytree("dashboard", os.path.join(dest_src, "dashboard"))
    
    # Clean and sync scripts
    if os.path.exists(os.path.join(dest_src, "scripts")):
        shutil.rmtree(os.path.join(dest_src, "scripts"))
    shutil.copytree("scripts", os.path.join(dest_src, "scripts"))
    
    # Clean and sync sql
    if os.path.exists(os.path.join(dest_src, "sql")):
        shutil.rmtree(os.path.join(dest_src, "sql"))
    shutil.copytree("sql", os.path.join(dest_src, "sql"))
    
    # Clean and sync notebooks
    if os.path.exists(os.path.join(dest_src, "notebooks")):
        shutil.rmtree(os.path.join(dest_src, "notebooks"))
    shutil.copytree("notebooks", os.path.join(dest_src, "notebooks"))
    
    # Clean and sync charts under Documentation
    dest_charts = os.path.join(sub_dir, "Documentation", "charts")
    if os.path.exists(dest_charts):
        shutil.rmtree(dest_charts)
    shutil.copytree("reports/charts", dest_charts)
    
    # Sync files
    files_to_copy = ["run_pipeline.py", "requirements.txt", "data_ingestion.py", "live_nav_fetch.py", "README.md"]
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy2(file, dest_src)
            
    print("Synchronization to vishaalnarigiri7745_submission completed successfully.\n")
 
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
    
    # 3b. Generate performance plots
    run_script("generate_performance_plots.py")
    
    # 4. Run advanced risk analytics
    run_script("advanced_analytics.py")
    
    # 4b. Generate EDA analysis notebook and charts
    run_script("generate_eda.py")
    
    # 5. Generate final PDF report
    run_script("generate_pdf_report.py")
    
    # 6. Generate final PPT presentation
    run_script("generate_presentation.py")
    
    # 6b. Capture dashboard screenshots and PDF
    run_script("capture_screenshots.py")
    
    # 7. Synchronize updated files to submission directory
    sync_submission_folder()
    
    print("=" * 80)
    print("ETL PIPELINE RUN COMPLETED SUCCESSFULLY!")
    print("All deliverables generated:")
    print(" - SQLite Database: db/bluestock_mf.db")
    print(" - Fund Scorecard: data/processed/fund_scorecard.csv")
    print(" - Alpha & Beta vs Nifty 100: data/processed/alpha_beta.csv")
    print(" - Tracking Errors: data/processed/tracking_error.csv")
    # Write a note about the Streamlit interactive dashboard replacing PBIX
    pbix_readme_path = "/Users/vaishnavnarigiri/Desktop/bluestock/vishaalnarigiri7745_submission/README_interactive_dashboard.txt"
    with open(pbix_readme_path, "w") as f:
        f.write("Bluestock Capstone Mutual Fund Analytics Dashboard:\n")
        f.write("The interactive dashboard is implemented using Streamlit instead of Power BI.\n")
        f.write("Source code can be found in Source_Code/dashboard/app.py.\n")
        f.write("To run the interactive dashboard, install requirements and execute:\n")
        f.write("    streamlit run Source_Code/dashboard/app.py\n")
        f.write("PDF export is available at Documentation/Dashboard.pdf.\n")
        f.write("Page screenshots are located in Documentation/charts/Page*.png.\n")
    print(" - Interactive Dashboard Note: README_interactive_dashboard.txt")
    print(" - PDF Dashboard Report: Documentation/Dashboard.pdf")
    print(" - Dashboard screenshots: Documentation/charts/Page*.png")
    print(" - Submission sync folder: vishaalnarigiri7745_submission/")
    print("=" * 80)

