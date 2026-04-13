import os
import tkinter as tk
from tkinter import messagebox
from src.constants import ERRORS
from src.gui.app import GuiApp
from src.core.config import Config
from src.services.schedule_utils import load_schedule
from src.services.file_utils import get_base_dir


BASE_DIR = get_base_dir(__file__)
CONFIGS_DIR = os.path.join(BASE_DIR, "configs")
PATHS = {
    'BASE_DIR': BASE_DIR,
    'CONFIG_FILE': os.path.join(CONFIGS_DIR, "config.json"),
    'SCHEDULE_FILE': os.path.join(CONFIGS_DIR, "schedule.json"),
    'SECRETS_FILE': os.path.join(CONFIGS_DIR, "client_secret.json"),
    'TOKEN_FILE': os.path.join(CONFIGS_DIR, "token.json"),
    'REPORTS_DIR': os.path.join(BASE_DIR, 'reports')
}

def main():
    if not os.path.exists(CONFIGS_DIR):
        os.makedirs(CONFIGS_DIR)

    if not os.path.exists(PATHS['SECRETS_FILE']):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Critical Error", 
            ERRORS['NO_SECRETS']
        )
        return

    config = Config(PATHS['CONFIG_FILE'], PATHS['REPORTS_DIR'])
    schedule = load_schedule(PATHS['SCHEDULE_FILE'])

    app = GuiApp(config, schedule, PATHS)
    app.mainloop()

if __name__ == "__main__":
    main()
