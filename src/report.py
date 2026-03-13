import datetime
import os


def create_report(report_dir: str, report_lines: str):
  today = datetime.datetime.now().strftime('%Y-%m-%d')

  report_path = os.path.join(report_dir, f"Youtube_Report_{today}.txt")
  with open(report_path, 'w', encoding='utf-8') as f:
      f.write(f"--- YouTube Upload Report for {today} ---\n\n")
      f.write("\n".join(report_lines))

  return report_path
