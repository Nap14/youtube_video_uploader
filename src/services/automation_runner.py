import threading
import os
import csv
from tkinter import filedialog
from ..core.engine import process_youtube, process_lms
from ..services.youtube.auth import Oauth2Service
from ..services.report_utils import create_report

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
        zoom_dir = app.config.get_zoom_dir()
        if not zoom_dir:
            logger.error("Zoom Directory is not set!")
            return

        mode = dash.mode_var.get()
        dash.start_btn.configure(state="disabled")
        try:
            oauth = Oauth2Service(logger)
            youtube = oauth.get_service(app.paths['TOKEN_FILE'], app.paths['SECRETS_FILE']) if mode in ["1", "2"] else None
            
            def cb(m, p): app.after(0, lambda: dash.progress_bar.set(p[0]/p[1]))
            
            yt_res = []
            if mode in ["1", "2"]:
                yt_res = process_youtube(app.config, app.schedule, youtube, logger, cb)
                if yt_res: create_report(yt_res, app.config.get_reports_dir(), f"{task_prefix}youtube")
            
            if mode == "3":
                f = filedialog.askopenfilename(title="Select YouTube CSV", filetypes=[("CSV", "*.csv")])
                if not f: return
                with open(f, mode='r', encoding='utf-8') as f_obj:
                    yt_res = list(csv.reader(f_obj))[1:]
                logger.info(f"Loaded {len(yt_res)} rows.")

            if mode in ["1", "3"]:
                lms_res = process_lms(yt_res, app.config, app.schedule, logger, cb)
                if lms_res: create_report(lms_res, app.config.get_reports_dir(), f"{task_prefix}lms")
            
            logger.info("Task Completed!")
            if task_prefix == "auto_": app.after(0, app.frames["planner"].refresh_history)
        except Exception as e: logger.error(f"Fatal: {e}")
        finally: app.after(0, lambda: dash.start_btn.configure(state="normal"))

    threading.Thread(target=run, daemon=True).start()
