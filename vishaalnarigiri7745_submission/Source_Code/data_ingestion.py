import os
import pandas as pd

raw_dir = "/Users/vaishnavnarigiri/Desktop/bluestock/data/raw"
report_path = "/Users/vaishnavnarigiri/Desktop/bluestock/reports/data_quality_summary.md"

files = sorted([f for f in os.listdir(raw_dir) if f.endswith('.csv')])

markdown_output = """# Data Quality Summary Report

This report summarizes the data quality analysis of the 10 raw mutual fund datasets.

"""

for filename in files:
    file_path = os.path.join(raw_dir, filename)
    print(f"Inspecting {filename}...")
    try:
        df = pd.read_csv(file_path)
        
        # Calculate stats
        rows, cols = df.shape
        missing = df.isnull().sum().to_dict()
        duplicates = df.duplicated().sum()
        dtypes = df.dtypes.to_dict()
        
        markdown_output += f"## {filename}\n\n"
        markdown_output += f"- **Shape**: {rows} rows, {cols} columns\n"
        markdown_output += f"- **Duplicate Rows**: {duplicates}\n\n"
        
        markdown_output += "### Data Types:\n"
        markdown_output += "| Column | Data Type |\n|---|---|\n"
        for col, dtype in dtypes.items():
            markdown_output += f"| {col} | {dtype} |\n"
        markdown_output += "\n"
        
        markdown_output += "### Missing Values:\n"
        if sum(missing.values()) == 0:
            markdown_output += "No missing values.\n\n"
        else:
            markdown_output += "| Column | Missing Count |\n|---|---|\n"
            for col, count in missing.items():
                if count > 0:
                    markdown_output += f"| {col} | {count} |\n"
            markdown_output += "\n"
            
        markdown_output += "### Sample Data (First 5 Rows):\n"
        markdown_output += df.head().to_markdown(index=False)
        markdown_output += "\n\n---\n\n"
        
    except Exception as e:
        markdown_output += f"## {filename}\nFailed to load: {e}\n\n---\n\n"

# Write report
with open(report_path, "w") as f:
    f.write(markdown_output)

print("Data quality summary report generated successfully.")
