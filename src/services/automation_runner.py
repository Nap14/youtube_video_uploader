import threading
from typing import Any, Protocol

from src.services.automation_core import AutomationCore

class TextWidget(Protocol):
    def configure(self, state: str) -> None: ...
    def insert(self, index: str, text: str) -> None: ...
    def see(self, index: str) -> None: ...
    def after(self, ms: int, func: Any) -> None: ...

class GuiLogger:
    def __init__(self, widget: TextWidget):
        self.widget = widget

    def info(self, m: str): 
        self._log(f"INFO: {m}")
        
    def error(self, m: str): 
        self._log(f"ERROR: {m}")
        
    def warning(self, m: str): 
        self._log(f"WARN: {m}")

    def _log(self, m: str):
        def update():
            self.widget.configure(state="normal")
            self.widget.insert("end", f"{m}\n")
            self.widget.see("end")
            self.widget.configure(state="disabled")
        self.widget.after(0, update)

def start_automation_task(app: Any, task_prefix: str = ""):
    def run():
        dash = app.frames["dashboard"]
        
        if not app.ctx.config.get_zoom_dir():
            app.ctx.logger.error("Zoom Directory is not set!")
            return
            
        mode = dash.mode_var.get()
        lms_csv = None
        if mode == "3":
            lms_csv = dash.lms_ent.get()
            
        if mode == "3" and not lms_csv:
            app.ctx.logger.error("Please select a YouTube CSV file!")
            return
            
        _execute_with_ui(app, dash, mode, lms_csv, task_prefix)

    threading.Thread(target=run, daemon=True).start()

def _execute_with_ui(app, dash, mode, lms_csv, task_prefix):
    dash.start_btn.configure(state="disabled")
    try:
        def cb(m: str, p: tuple):
            app.after(0, lambda: dash.progress_bar.set(p[0]/p[1]))
            if m:
                app.ctx.logger.info(m)
            
        automation = AutomationCore(app.ctx, cb, error_cb=app.show_error)
        automation.execute_automation(mode, lms_csv_path=lms_csv, task_prefix=task_prefix)
        
        app.after(0, dash.refresh)
        if task_prefix == "auto_":
            app.after(0, app.frames["planner"].refresh)
    except Exception as e:
        app.ctx.logger.error(f"Fatal Error: {e}")
    finally:
        app.after(0, lambda: dash.start_btn.configure(state="normal"))
