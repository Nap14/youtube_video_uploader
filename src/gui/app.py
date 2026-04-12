import customtkinter as ctk
import json
from .sidebar import Sidebar
from .dashboard import DashboardFrame
from .settings import SettingsFrame
from .schedule import ScheduleCalendarFrame
from .reports import ReportsFrame
from .modals import LessonEditModal

class GuiApp(ctk.CTk):
    def __init__(self, config, schedule, paths):
        super().__init__()
        self.config, self.schedule, self.paths = config, schedule, paths
        self.title("Zoom Video Automation")
        self.geometry("1100x600")
        self.minsize(900, 500)
        
        # Theme setup
        self.theme = self.config.get_data().get("THEME", "Dark")
        ctk.set_appearance_mode(self.theme)
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.setup_ui()

    def setup_ui(self):
        self.sidebar = Sidebar(self, self.select_frame, self.change_theme, self.theme, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.frames = {
            "dashboard": DashboardFrame(self, self.start_automation, fg_color="transparent"),
            "settings": SettingsFrame(self, self.config, self.paths, self.browse_dir, self.save_settings, fg_color="transparent"),
            "schedule": ScheduleCalendarFrame(self, self.schedule, self.open_edit, fg_color="transparent"),
            "reports": ReportsFrame(self, self.config, fg_color="transparent")
        }
        self.select_frame("dashboard")

    def select_frame(self, name):
        for f in self.frames.values(): f.grid_forget()
        self.frames[name].grid(row=0, column=1, sticky="nsew")
        self.sidebar.highlight_button(name)
        if name == "schedule": self.frames[name].refresh()
        if name == "reports": self.frames[name].refresh_reports()

    def change_theme(self, mode):
        ctk.set_appearance_mode(mode)
        self.config.get_data()["THEME"] = mode
        self.config.save()

    def open_edit(self, d=None, t=None, v=None):
        LessonEditModal(self, self.schedule, d, t, v, on_save=self.on_schedule_save)

    def on_schedule_save(self):
        try:
            with open(self.paths['SCHEDULE_FILE'], 'w', encoding='utf-8') as f:
                json.dump(self.schedule, f, ensure_ascii=False, indent=4)
            self.frames["schedule"].refresh()
        except Exception as e: print(f"Save error: {e}")

    def browse_dir(self):
        from tkinter import filedialog
        d = filedialog.askdirectory(initialdir=self.frames["settings"].zoom_dir_entry.get())
        if d: self.frames["settings"].zoom_dir_entry.delete(0, "end"); self.frames["settings"].zoom_dir_entry.insert(0, d)

    def save_settings(self):
        f = self.frames["settings"]
        self.config.get_data().update({"ZOOM_DIR": f.zoom_dir_entry.get(), "LMS_TOKEN": f.lms_token_entry.get(), 
                                      "SCHOOL_ID": f.school_id_entry.get()})
        self.config.save()

    def start_automation(self):
        import threading
        from ..core.engine import process_youtube, process_lms
        from ..services.youtube.auth import Oauth2Service
        from ..services.report_utils import create_report

        def run():
            logger = GuiLogger(self.frames["dashboard"].log_text)
            mode = self.frames["dashboard"].mode_var.get()
            self.frames["dashboard"].start_btn.configure(state="disabled")
            
            try:
                oauth = Oauth2Service(logger)
                youtube = None
                if mode in ["1", "2"]:
                    youtube = oauth.get_service(self.paths['TOKEN_FILE'], self.paths['SECRETS_FILE'])
                
                def cb(m, p): self.after(0, lambda: self.frames["dashboard"].progress_bar.set(p[0]/p[1]))
                
                yt_res = []
                if mode in ["1", "2"]:
                    yt_res = process_youtube(self.config, self.schedule, youtube, logger, cb)
                    if yt_res: create_report(yt_res, self.config.get_reports_dir(), "youtube")
                
                if mode == "3":
                    from tkinter import filedialog
                    import csv
                    file_path = filedialog.askopenfilename(title="Select YouTube Report CSV", filetypes=[("CSV Files", "*.csv")])
                    if not file_path:
                        logger.warning("No file selected. LMS sync aborted.")
                        return
                    with open(file_path, mode='r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader) # skip header
                        yt_res = list(reader)
                    logger.info(f"Loaded {len(yt_res)} rows from {os.path.basename(file_path)}")

                if mode in ["1", "3"]:
                    lms_res = process_lms(yt_res, self.config, self.schedule, logger, cb)
                    if lms_res: create_report(lms_res, self.config.get_reports_dir(), "lms")
                
                logger.info("Task Completed!")
            except Exception as e: logger.error(f"Fatal: {e}")
            finally: self.after(0, lambda: self.frames["dashboard"].start_btn.configure(state="normal"))

        threading.Thread(target=run, daemon=True).start()

class GuiLogger:
    def __init__(self, text_widget): self.text_widget = text_widget
    def info(self, m): self._log(f"INFO: {m}")
    def error(self, m): self._log(f"ERROR: {m}")
    def warning(self, m): self._log(f"WARN: {m}")
    def _log(self, m):
        self.text_widget.configure(state="normal")
        self.text_widget.insert("end", f"{m}\n"); self.text_widget.see("end")
        self.text_widget.configure(state="disabled")
