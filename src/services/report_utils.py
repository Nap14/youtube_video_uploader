import csv
import os
from datetime import datetime

def create_report(report_rows, reports_dir, prefix="report"):
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
        
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(reports_dir, f"{prefix}_{ts}.csv")
    
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Date", "Course", "URL", "Status", "Details"])
        writer.writerows(report_rows)
    
    # Also create a .txt summary
    txt_path = os.path.join(reports_dir, f"{prefix}_{ts}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"=== {prefix.upper()} REPORT - {ts} ===\n\n")
        for row in report_rows:
            f.write(f"Date: {row[0]}\nCourse: {row[1]}\nURL: {row[2]}\nStatus: {row[3]}\n{'-'*20}\n")
            
    return path
