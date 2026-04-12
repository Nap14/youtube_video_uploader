import datetime
import os
import csv

def create_report(report_dir: str, data_rows: list, report_type: str = "youtube"):
    """
    Creates reports in the specified directory.
    YouTube reports get both CSV (for machine sync) and TXT (for user viewing).
    """
    if not os.path.exists(report_dir):
        os.makedirs(report_dir, exist_ok=True)

    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    today_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    csv_filename = f"{report_type}_report_{timestamp}.csv"
    csv_path = os.path.join(report_dir, csv_filename)

    if report_type == "youtube":
        header = ["Date", "Course", "YouTube URL", "Status"]
    else:
        header = ["Date", "Course", "LMS Status", "Message"]

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data_rows)

    if report_type == "youtube":
        txt_filename = f"Youtube_Report_{today_date}.txt"
        txt_path = os.path.join(report_dir, txt_filename)
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(f"--- YouTube Upload Report for {today_date} ---\n\n")
            for row in data_rows:
                date_str, course, url, status = row
                f.write(f"{date_str} | {course} | Link: {url} ({status})\n")
        
        return txt_path

    return csv_path
