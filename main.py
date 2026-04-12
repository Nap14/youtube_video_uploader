import os
from src.core.config import Config
from src.services.schedule_utils import load_schedule

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIGS_DIR = os.path.join(BASE_DIR, "configs")
PATHS = {
    'CONFIG_FILE': os.path.join(CONFIGS_DIR, "config.json"),
    'SCHEDULE_FILE': os.path.join(CONFIGS_DIR, "schedule.json"),
    'SECRETS_FILE': os.path.join(CONFIGS_DIR, "client_secret.json"),
    'TOKEN_FILE': os.path.join(CONFIGS_DIR, "token.json"),
    'REPORTS_DIR': os.path.join(BASE_DIR, 'reports')
}

def main():
    # Pre-boot check for client_secret.json
    if not os.path.exists(PATHS['SECRETS_FILE']):
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk(); root.withdraw()
        messagebox.showerror("Critical Error", "Файл 'client_secret.json' не знайдено!")
        return

    config = Config(PATHS['CONFIG_FILE'], PATHS['REPORTS_DIR'])
    schedule = load_schedule(PATHS['SCHEDULE_FILE'])

    from src.gui.app import GuiApp
    app = GuiApp(config, schedule, PATHS)
    app.mainloop()

if __name__ == "__main__":
    main()
