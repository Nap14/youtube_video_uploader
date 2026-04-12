import os
import argparse
import logging
from src.core.config import Config
from src.services.schedule_utils import load_schedule
from src.services.youtube.auth import Oauth2Service
from src.services.report_utils import create_report
from src.core.engine import process_youtube, process_lms

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIGS_DIR = os.path.join(BASE_DIR, "configs")
PATHS = {
    'CONFIG_FILE': os.path.join(CONFIGS_DIR, "config.json"),
    'SCHEDULE_FILE': os.path.join(CONFIGS_DIR, "schedule.json"),
    'SECRETS_FILE': os.path.join(CONFIGS_DIR, "client_secret.json"),
    'TOKEN_FILE': os.path.join(CONFIGS_DIR, "token.json")
}

def run_cli(config, schedule):
    logger = logging.getLogger("CLI")
    oauth = Oauth2Service(logger)
    youtube = oauth.get_service(PATHS['TOKEN_FILE'], PATHS['SECRETS_FILE'])
    
    yt_reports = process_youtube(config, schedule, youtube, logger)
    lms_reports = process_lms(yt_reports, config, schedule, logger)
    
    reports_dir = config.get_reports_dir()
    create_report(yt_reports, reports_dir, "youtube")
    if lms_reports: create_report(lms_reports, reports_dir, "lms")

def main():
    parser = argparse.ArgumentParser(description="Zoom Video Automation")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    # Pre-boot check for client_secret.json
    if not os.path.exists(PATHS['SECRETS_FILE']):
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Critical Error", "Файл 'client_secret.json' не знайдено у папці configs!\nБудь ласка, зверніться до адміністратора додатку.")
        return

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    config = Config(PATHS['CONFIG_FILE'], logging)
    schedule = load_schedule(PATHS['SCHEDULE_FILE'])

    if args.cli:
        run_cli(config, schedule)
    else:
        from src.gui.app import GuiApp
        app = GuiApp(config, schedule, PATHS)
        app.mainloop()

if __name__ == "__main__":
    main()
