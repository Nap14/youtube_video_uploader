import queue
import threading
from typing import Any, Callable, Optional

from src.core.context import AppContext
from src.core.logger import Logger
from src.services.automation_core import AutomationCore

class QueueLogger:
    """Thread-safe logger that sends text messages to the UI queue without referencing any Tk widgets."""
    def __init__(self, q: queue.Queue):
        self.q = q

    def info(self, m: str) -> None:
        print(f"INFO: {m}")
        self.q.put(("log", f"INFO: {m}"))

    def error(self, m: str) -> None:
        print(f"ERROR: {m}")
        self.q.put(("log", f"ERROR: {m}"))

    def warning(self, m: str) -> None:
        print(f"WARN: {m}")
        self.q.put(("log", f"WARN: {m}"))

class GuiLogger(QueueLogger):
    """Backwards-compatible wrapper around QueueLogger."""
    def __init__(self, widget: Any = None, post_fn: Optional[Callable] = None, q: Optional[queue.Queue] = None):
        if q is not None:
            super().__init__(q)
        else:
            self.widget = widget
            self.post_fn = post_fn
            self.q = None

    def _log(self, m: str):
        print(m)
        if self.q is not None:
            self.q.put(("log", m))
        elif self.post_fn is not None:
            self.post_fn(lambda: self._direct_insert(m))

    def _direct_insert(self, m: str):
        if self.widget:
            try:
                self.widget.configure(state="normal")
                self.widget.insert("end", f"{m}\n")
                self.widget.see("end")
                self.widget.configure(state="disabled")
            except Exception:
                pass


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

    ui_queue: queue.Queue = app._ui_queue
    ctx: AppContext = app.ctx

    def run():
        _execute_in_background(ctx, ui_queue, mode, lms_csv, task_prefix)

    threading.Thread(target=run, daemon=True).start()


def _execute_in_background(ctx: AppContext, ui_queue: queue.Queue, mode: str, lms_csv: Optional[str], task_prefix: str):
    """Executes automation in a background thread completely decoupled from Tkinter.
    
    NO Tkinter widget references, closures capturing widgets, or GUI objects exist in this thread.
    All communication with UI happens exclusively via queue messages with primitive values.
    """
    try:
        def cb(m: str, p: tuple):
            if p and len(p) >= 2 and p[1] > 0:
                val = max(0.0, min(1.0, float(p[0]) / float(p[1])))
                ui_queue.put(("progress", val))
            if m:
                ctx.logger.info(m)

        def on_error(title: str, msg: str):
            ui_queue.put(("error", (title, msg)))

        automation = AutomationCore(ctx, cb, error_cb=on_error)
        automation.execute_automation(mode, lms_csv_path=lms_csv, task_prefix=task_prefix)

    except Exception as e:
        ctx.logger.error(f"Fatal Error: {e}")
    finally:
        ui_queue.put(("done", task_prefix))
