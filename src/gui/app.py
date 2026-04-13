import customtkinter as ctk
import json, csv
from .sidebar import Sidebar
from .dashboard import DashboardFrame
from .settings import SettingsFrame
from .schedule import ScheduleCalendarFrame
from .reports import ReportsFrame
from .modals.lesson import LessonEditModal
from .planner import PlannerFrame
from .tray_manager import TrayManager
from ..core.scheduler import SchedulerService
from ..services.automation_runner import start_automation_task

class GuiApp(ctk.CTk):
    def __init__(self, config, schedule, paths):
        super().__init__()
        self.config, self.schedule, self.paths = config, schedule, paths
        self.title("Zoom Video Automation")
        self.geometry("1100x600")
        self.minsize(900, 500)
        ctk.set_appearance_mode(self.config.get_data().get("THEME", "Dark"))
        self.grid_columnconfigure(1, weight=1); self.grid_rowconfigure(0, weight=1)
        self.setup_ui()
        self.scheduler = SchedulerService(self.config, self.trigger_automation)
        self.scheduler.start()
        self.tray = TrayManager(self, self.exit_app)
        self.protocol("WM_DELETE_WINDOW", lambda: self.withdraw())

    def setup_ui(self):
        self.sidebar = Sidebar(self, self.select_frame, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.frames = {
            "dashboard": DashboardFrame(self, self.config, self.start_automation, self.browse_lms_file, self.view_report, fg_color="transparent"),
            "settings": SettingsFrame(self, self.config, self.paths, self.browse_dir, self.save_settings, self.change_theme, fg_color="transparent"),
            "schedule": ScheduleCalendarFrame(self, self.schedule, self.open_edit, fg_color="transparent"),
            "reports": ReportsFrame(self, self.config, fg_color="transparent"),
            "planner": PlannerFrame(self, self.config, fg_color="transparent")
        }
        self.select_frame("settings" if not self.config.get_zoom_dir() else "dashboard")

    def trigger_automation(self, mode):
        def start_now():
            self.frames["dashboard"].mode_var.set(mode)
            self.start_automation(task_prefix="auto_")
        if self.config.get_planner_config().get("require_confirmation"):
            from tkinter import messagebox
            msg = f"Scheduled task (Mode {mode}) is about to start. Proceed?"
            self.after(0, lambda: messagebox.askyesno("Planner", msg) and start_now())
        else: self.after(0, start_now)

    def select_frame(self, name):
        curr = getattr(self, "_current_frame", None)
        if curr == "settings" and name != "settings" and self.frames["settings"].is_dirty():
            from tkinter import messagebox
            if messagebox.askyesno("Save?", "Save changes?"): self.save_settings()
        for f in self.frames.values(): f.grid_forget()
        self.frames[name].grid(row=0, column=1, sticky="nsew")
        self._current_frame = name; self.sidebar.highlight_button(name)
        c = {"schedule": "refresh", "reports": "refresh_reports", "planner": "refresh_history", "dashboard": "refresh"}
        if name in c: getattr(self.frames[name], c[name])()

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode); self.config.get_data()["THEME"] = mode; self.config.save()

    def open_edit(self, d=None, t=None, v=None):
        LessonEditModal(self, self.schedule, d, t, v, on_save=self.on_schedule_save)

    def on_schedule_save(self):
        with open(self.paths['SCHEDULE_FILE'], 'w', encoding='utf-8') as f:
            json.dump(self.schedule, f, ensure_ascii=False, indent=4)
        self.frames["schedule"].refresh()

    def browse_dir(self):
        from tkinter import filedialog
        d = filedialog.askdirectory(initialdir=self.frames["settings"].zoom_dir_entry.get())
        if d: 
            self.frames["settings"].zoom_dir_entry.delete(0, "end"); self.frames["settings"].zoom_dir_entry.insert(0, d)

    def save_settings(self):
        f = self.frames["settings"]
        self.config.get_data().update({"ZOOM_DIR": f.zoom_dir_entry.get(), "LMS_TOKEN": f.lms_token_entry.get(), "SCHOOL_ID": f.school_id_entry.get()})
        self.config.save(); f.show_status("Saved!")

    def start_automation(self, task_prefix=""): start_automation_task(self, task_prefix)

    def browse_lms_file(self):
        from tkinter import filedialog, messagebox
        f = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not f: return
        try:
            with open(f, 'r', encoding='utf-8') as file:
                if not list(csv.reader(file)): raise ValueError("Empty")
            dash = self.frames["dashboard"]
            dash.lms_file_entry.delete(0, "end"); dash.lms_file_entry.insert(0, f); dash.update_start_state()
        except Exception as e: messagebox.showerror("Error", f"Invalid file: {e}")

    def view_report(self, path):
        from .viewer import ReportTableModal
        ReportTableModal(self, path)

    def exit_app(self): 
        self.scheduler.stop()
        self.tray.stop()
        self.quit()
