import queue
import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any, Callable

from src.core.context import AppContext
from src.core.scheduler import SchedulerService
from src.services.automation_runner import start_automation_task, GuiLogger
from src.services.ui_service import UIService
from .dashboard import DashboardFrame
from .planner import PlannerFrame
from .reports import ReportsFrame
from .schedule import ScheduleCalendarFrame
from .settings import SettingsFrame
from .sidebar import Sidebar
from .tray_manager import TrayManager

class GuiApp(ctk.CTk):
    def __init__(self, ctx: AppContext):
        super().__init__()
        self.ctx = ctx
        self._ui_queue: queue.Queue = queue.Queue()
        self._poll_ui_queue()
        
        UIService.set_handler(self)
        self._setup_window()
        self._setup_ui()
        
        self.ctx.logger = GuiLogger(self.frames["dashboard"].log_text, post_fn=self.post_to_ui)
        
        self.scheduler = SchedulerService(self.ctx.config.get_planner_config(), self.trigger_automation, self.ctx.logger)
        self.scheduler.start()
        
        self.tray = TrayManager(self, self.exit_app)
        if self.tray.is_active():
            self.protocol("WM_DELETE_WINDOW", self.withdraw)
        else:
            self.protocol("WM_DELETE_WINDOW", self.exit_app)

    def _setup_window(self):
        self.title("Zoom Video Automation")
        self.geometry("1100x600")
        self.minsize(900, 500)
        
        app_data = self.ctx.config.get_data()
        ctk.set_appearance_mode(app_data.get("THEME", "Dark"))
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

    def _setup_ui(self):
        self._init_sidebar()
        self._init_frames()
        
        initial = "dashboard"
        if not self.ctx.config.get_zoom_dir():
            initial = "settings"
            
        self.select_frame(initial)

    def _init_sidebar(self):
        self.sidebar = Sidebar(self, self.select_frame, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

    def _init_frames(self):
        self.frames: Dict[str, Any] = {
            "dashboard": DashboardFrame(self, self.ctx, self.start_automation, fg_color="transparent"),
            "settings": SettingsFrame(self, self.ctx, fg_color="transparent"),
            "schedule": ScheduleCalendarFrame(self, self.ctx, fg_color="transparent"),
            "reports": ReportsFrame(self, self.ctx, fg_color="transparent"),
            "planner": PlannerFrame(self, self.ctx, fg_color="transparent")
        }

    def post_to_ui(self, func: Callable, *args: Any):
        """Thread-safe mechanism to schedule UI operations on the Tk main thread."""
        self._ui_queue.put((func, args))

    def _poll_ui_queue(self):
        try:
            while True:
                func, args = self._ui_queue.get_nowait()
                try:
                    func(*args)
                except Exception as e:
                    print(f"[UI Queue Error] {e}")
        except queue.Empty:
            pass
        finally:
            self.after(25, self._poll_ui_queue)

    def show_error(self, title, message):
        self.post_to_ui(lambda: messagebox.showerror(title, message))

    def show_info(self, title, message):
        self.post_to_ui(lambda: messagebox.showinfo(title, message))

    def trigger_automation(self, mode: str):
        p_cfg = self.ctx.config.get_planner_config()
        
        def start():
            self.frames["dashboard"].mode_var.set(mode)
            self.start_automation(task_prefix="auto_")
            
        if p_cfg.get("require_confirmation"):
            self.post_to_ui(lambda: messagebox.askyesno("Planner", f"Start Mode {mode}?") and start())
        else:
            self.post_to_ui(start)

    def select_frame(self, name: str):
        if name not in self.frames:
            return
            
        for f in self.frames.values():
            f.grid_forget()
            
        self.frames[name].grid(row=0, column=1, sticky="nsew")
        self.sidebar.highlight_button(name)
        self.frames[name].refresh()

    def start_automation(self, task_prefix: str = ""):
        start_automation_task(self, task_prefix)

    def exit_app(self): 
        try:
            self.scheduler.stop()
        except Exception:
            pass
        try:
            self.tray.stop()
        except Exception:
            pass
        try:
            self.quit()
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            pass
