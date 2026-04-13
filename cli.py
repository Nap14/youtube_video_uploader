from src.services.schedule_utils import load_schedule
import sys
import os

from src.core.config import Config
from src.constants import ERRORS
from src.services.automation_core import AutomationCore
from src.services.console_loger import ConsoleLogger
from src.services.file_utils import get_base_dir

BASE_DIR = get_base_dir(__file__)
CONFIGS_DIR = os.path.join(BASE_DIR, 'configs')

    
PATHS = {
    'BASE_DIR': BASE_DIR,
    'CONFIG_DIR': CONFIGS_DIR,
    'CONFIG_FILE': os.path.join(CONFIGS_DIR, 'config.json'),
    'SCHEDULE_FILE': os.path.join(CONFIGS_DIR, 'schedule.json'),
    'TOKEN_FILE': os.path.join(CONFIGS_DIR, 'token.json'),
    'SECRETS_FILE': os.path.join(CONFIGS_DIR, 'client_secret.json'),
    'REPORTS_DIR': os.path.join(BASE_DIR, 'reports')
}

config = Config(PATHS['CONFIG_FILE'], PATHS['REPORTS_DIR'])

def progress_cb(msg, p):
    sys.stdout.write(f"\rProgress: [{p[0]}/{p[1]}] {msg} ".ljust(80))
    sys.stdout.flush()

    if p[0] == p[1]: 
        print("\n")

def get_choice():
    print("Select Mode:")
    print("1. YouTube Upload + LMS Sync")
    print("2. YouTube Upload Only")
    print("3. LMS Sync from YouTube CSV")
    print("Q. Quit")
    
    choice = input("\nEnter choice (1-3 or Q): ").strip().upper()

    if choice == 'Q': 
        return

    if choice not in ['1', '2', '3']:
        print("Invalid choice.")
        return

    return choice

def main():
    print("\n=== Zoom Video Automation (Terminal Version) ===\n")

    if not os.path.exists(CONFIGS_DIR):
        os.makedirs(CONFIGS_DIR)
    
    if not os.path.exists(PATHS['SECRETS_FILE']):
        print(f"[ERROR] {ERRORS['NO_SECRETS']} (expected at {CONFIGS_DIR})")
        print("Please contact your administrator for detailed configuration information.")
        input("\nPress Enter to exit...")
        return

    choice = get_choice()
    if not choice: return

    lms_csv = None
    if choice == '3':
        lms_csv = input("Enter path to YouTube CSV report: ").strip()
        if not os.path.exists(lms_csv):
            print(f"Error: File {lms_csv} does not exist.")
            return

    logger = ConsoleLogger()
    schedule = load_schedule(PATHS['SCHEDULE_FILE'])

    try:
        automation = AutomationCore(config, schedule, PATHS, logger, progress_cb, error_cb=lambda t, m: logger.error(f"{t}: {m}"))
        automation.execute_automation(choice, lms_csv_path=lms_csv)
    except Exception as e:
        print(f"\n[FATAL] {e}")

if __name__ == "__main__":
    main()
