import threading
from tkinter import filedialog
from .automation_core import execute_automation

class GuiLogger:
    def __init__(self, text_widget): self.text_widget = text_widget
    def info(self, m): self._log(f"INFO: {m}")
    def error(self, m): self._log(f"ERROR: {m}")
    def warning(self, m): self._log(f"WARN: {m}")
    def _log(self, m):
        def update():
            self.text_widget.configure(state="normal")
            self.text_widget.insert("end", f"{m}\n")
            self.text_widget.see("end")
            self.text_widget.configure(state="disabled")
        self.text_widget.after(0, update)

def start_automation_task(app, task_prefix=""):
    def run():
        dash = app.frames["dashboard"]
        logger = GuiLogger(dash.log_text)
        if not app.config.get_zoom_dir():
            logger.error("Zoom Directory is not set!"); return

        mode = dash.mode_var.get()
        lms_csv = None
        if mode == "3":
            lms_csv = filedialog.askopenfilename(title="Select YouTube CSV", filetypes=[("CSV", "*.csv")])
            if not lms_csv: return

        dash.start_btn.configure(state="disabled")
        try:
            def cb(m, p): app.after(0, lambda: dash.progress_bar.set(p[0]/p[1]))
            execute_automation(app.config, app.schedule, app.paths, mode, logger, cb, 
                               lms_csv_path=lms_csv, task_prefix=task_prefix)
            if task_prefix == "auto_": app.after(0, app.frames["planner"].refresh_history)
        except Exception as e: logger.error(f"Fatal Error: {e}")
        finally: app.after(0, lambda: dash.start_btn.configure(state="normal"))

    threading.Thread(target=run, daemon=True).start()
