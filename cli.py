import sys
import os
import json
from src.core.config import Config
from src.services.automation_core import execute_automation

class ConsoleLogger:
    def info(self, m): print(f"[INFO] {m}")
    def error(self, m): print(f"[ERROR] {m}")
    def warning(self, m): print(f"[WARN] {m}")

def main():
    print("\n=== Zoom Video Automation (Terminal Version) ===\n")
    
    # Load paths and config
    base_path = os.path.dirname(os.path.abspath(__file__))
    paths = {
        'CONFIG_DIR': os.path.join(base_path, 'configs'),
        'CONFIG_FILE': os.path.join(base_path, 'configs', 'config.json'),
        'SCHEDULE_FILE': os.path.join(base_path, 'configs', 'schedule.json'),
        'TOKEN_FILE': os.path.join(base_path, 'configs', 'token.json'),
        'SECRETS_FILE': os.path.join(base_path, 'configs', 'client_secret.json'),
        'REPORTS_DIR': os.path.join(base_path, 'reports')
    }
    
    config = Config(paths['CONFIG_FILE'], paths['REPORTS_DIR'])
    if not os.path.exists(paths['SCHEDULE_FILE']):
        print(f"[ERROR] Schedule file not found at {paths['SCHEDULE_FILE']}")
        return
    with open(paths['SCHEDULE_FILE'], 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    print("Select Mode:")
    print("1. YouTube Upload + LMS Sync")
    print("2. YouTube Upload Only")
    print("3. LMS Sync from YouTube CSV")
    print("Q. Quit")
    
    choice = input("\nEnter choice (1-3 or Q): ").strip().upper()
    if choice == 'Q': return
    if choice not in ['1', '2', '3']:
        print("Invalid choice.")
        return

    lms_csv = None
    if choice == '3':
        lms_csv = input("Enter path to YouTube CSV report: ").strip()
        if not os.path.exists(lms_csv):
            print(f"Error: File {lms_csv} does not exist.")
            return

    logger = ConsoleLogger()
    def progress_cb(msg, p):
        sys.stdout.write(f"\rProgress: [{p[0]}/{p[1]}] {msg} ".ljust(80))
        sys.stdout.flush()
        if p[0] == p[1]: print("\n")

    try:
        execute_automation(config, schedule, paths, choice, logger, progress_cb, lms_csv_path=lms_csv)
    except Exception as e:
        print(f"\n[FATAL] {e}")

if __name__ == "__main__":
    main()
