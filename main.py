import os
import sys
import traceback
import tkinter as tk

from src.core.path_manager import PathManager
from src.core.config import Config
from src.core.context import AppContext
from src.gui.app import GuiApp
from src.services.schedule_utils import load_schedule
from src.services.bootstrapper import Bootstrapper
from src.services.console_loger import ConsoleLogger


def show_fatal_error(title: str, message: str, details: str = ""):
    """Save error to log files and present an interactive error window to the user."""
    # Write to crash log on Desktop and in current folder
    desktop_log = os.path.join(os.path.expanduser("~"), "Desktop", "ZoomAutomation_crash.log")
    local_log = os.path.join(os.getcwd(), "crash.log")
    
    log_text = f"=== {title} ===\n{message}\n\nTraceback:\n{details}\n"
    for path in (desktop_log, local_log):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(log_text)
        except Exception:
            pass

    try:
        root = tk.Tk()
        root.title(title)
        root.geometry("680x480")
        root.minsize(500, 320)
        root.lift()
        root.attributes("-topmost", True)

        header = tk.Label(root, text="Сталася помилка при запуску:", font=("Arial", 13, "bold"), fg="#c0392b")
        header.pack(padx=20, pady=(20, 5), anchor="w")

        msg_lbl = tk.Label(root, text=message, font=("Arial", 11), wraplength=640, justify="left")
        msg_lbl.pack(padx=20, pady=(0, 10), anchor="w")

        info_lbl = tk.Label(root, text=f"Детальний лог збережено на Робочий стіл:\n{desktop_log}", font=("Arial", 10, "italic"), fg="gray40", justify="left")
        info_lbl.pack(padx=20, pady=(0, 10), anchor="w")

        if details:
            txt_frame = tk.Frame(root)
            txt_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

            scrollbar = tk.Scrollbar(txt_frame)
            scrollbar.pack(side="right", fill="y")

            txt = tk.Text(txt_frame, wrap="none", yscrollcommand=scrollbar.set, font=("Courier", 10))
            txt.insert("1.0", details)
            txt.configure(state="disabled")
            txt.pack(side="left", fill="both", expand=True)
            scrollbar.config(command=txt.yview)

        btn_frame = tk.Frame(root)
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        def copy_err():
            root.clipboard_clear()
            root.clipboard_append(f"{message}\n\n{details}")
            copy_btn.config(text="Скопійовано! ✓")

        copy_btn = tk.Button(btn_frame, text="Скопіювати помилку", command=copy_err, width=18)
        copy_btn.pack(side="left")

        close_btn = tk.Button(btn_frame, text="Закрити", command=root.destroy, width=12)
        close_btn.pack(side="right")

        root.mainloop()
    except Exception as e:
        print(f"[FATAL ERROR] {message}\n{details}\n(Error dialog failed: {e})", file=sys.stderr)


def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    err_tb = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    show_fatal_error(
        "Zoom Video Automation - Помилка",
        f"{exc_value}",
        err_tb
    )

sys.excepthook = global_exception_handler


def main():
    try:
        pm = PathManager(__file__)
        paths = pm.get_paths()

        # Гарантуємо, що робоча директорія відповідає розташуванню додатку
        # (при запуску з Finder macOS встановлює робочу директорію в /)
        try:
            os.chdir(paths.base_dir)
        except Exception as e:
            print(f"[WARN] Failed to change dir to {paths.base_dir}: {e}")

        pm.ensure_dirs()

        if not Bootstrapper.validate_gui_env(paths):
            return

        config = Config(paths.config_file, paths.reports_dir)
        schedule = load_schedule(paths.schedule_file)
        
        ctx = AppContext(
            config=config, 
            schedule=schedule, 
            paths=paths, 
            logger=ConsoleLogger()
        )

        app = GuiApp(ctx)
        app.mainloop()
    except Exception as e:
        err_tb = traceback.format_exc()
        show_fatal_error(
            "Zoom Video Automation - Помилка",
            f"Не вдалося запустити додаток: {e}",
            err_tb
        )

if __name__ == "__main__":
    main()
