import csv
import os
from datetime import datetime

def create_report(report_rows, reports_dir, prefix="report", headers=None):
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir, exist_ok=True)
        
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(reports_dir, f"{prefix}_{ts}.csv")
    
    if not headers:
        headers = ["Date", "Course", "URL", "Status", "Details"]

    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(report_rows)
    
    txt_path = os.path.join(reports_dir, f"{prefix}_{ts}.txt")
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(f"=== {prefix.upper()} REPORT - {ts} ===\n\n")
        for row in report_rows:
            f.write(f"Date: {row[0]}\nCourse: {row[1]}\nURL: {row[2]}\nStatus: {row[3]}\n{'-'*20}\n")
            
    return path

def list_reports(reports_dir):
    if not os.path.exists(reports_dir): return []
    files = [f for f in os.listdir(reports_dir) if f.endswith((".csv", ".txt"))]
    files.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
    return files

def get_latest_report(reports_dir):
    files = list_reports(reports_dir)
    for f in files:
        if f.endswith(".csv"): return os.path.join(reports_dir, f)
    return None
