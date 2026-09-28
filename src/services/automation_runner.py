import threading
from typing import Any, Callable, Optional, Protocol

from src.services.automation_core import AutomationCore

class TextWidget(Protocol):
    def configure(self, state: str) -> None: ...
    def insert(self, index: str, text: str) -> None: ...
    def see(self, index: str) -> None: ...

class GuiLogger:
    def __init__(self, widget: TextWidget, post_fn: Optional[Callable[[Callable], None]] = None):
        self.widget = widget
        self.post_fn = post_fn

    def info(self, m: str): 
        self._log(f"INFO: {m}")
        
    def error(self, m: str): 
        self._log(f"ERROR: {m}")
        
    def warning(self, m: str): 
        self._log(f"WARN: {m}")

    def _log(self, m: str):
        print(m)
        def update():
            try:
                self.widget.configure(state="normal")
                self.widget.insert("end", f"{m}\n")
                self.widget.see("end")
                self.widget.configure(state="disabled")
            except Exception:
                pass

        if self.post_fn:
            self.post_fn(update)
        elif hasattr(self.widget, "after"):
            self.widget.after(0, update)
        else:
            update()

def start_automation_task(app: Any, task_prefix: str = ""):
    dash = app.frames["dashboard"]
    
    if not app.ctx.config.get_zoom_dir():
        app.ctx.logger.error("Zoom Directory is not set! Please check Settings.")
        return
        
    mode = dash.mode_var.get()
    lms_csv = None
    if mode == "3":
        lms_csv = dash.lms_ent.get()
        
    if mode == "3" and not lms_csv:
        app.ctx.logger.error("Please select a YouTube CSV file!")
        return
        
    # Disable button and reset progress bar on main thread before launching background worker
    dash.start_btn.configure(state="disabled")
    dash.progress_bar.set(0)
    app.ctx.logger.info(f"Starting automation task (Mode {mode})...")

    def run():
        _execute_with_ui(app, dash, mode, lms_csv, task_prefix)

    threading.Thread(target=run, daemon=True).start()

def _execute_with_ui(app, dash, mode, lms_csv, task_prefix):
    dispatch = getattr(app, "post_to_ui", lambda fn: app.after(0, fn))
    try:
        def cb(m: str, p: tuple):
            if p and len(p) >= 2 and p[1] > 0:
                val = max(0.0, min(1.0, float(p[0]) / float(p[1])))
                dispatch(lambda: dash.progress_bar.set(val))
            if m:
                app.ctx.logger.info(m)
            
        automation = AutomationCore(app.ctx, cb, error_cb=app.show_error)
        automation.execute_automation(mode, lms_csv_path=lms_csv, task_prefix=task_prefix)
        
        dispatch(dash.refresh)
        if task_prefix == "auto_":
            dispatch(app.frames["planner"].refresh)
    except Exception as e:
        app.ctx.logger.error(f"Fatal Error: {e}")
    finally:
        dispatch(lambda: dash.start_btn.configure(state="normal"))
