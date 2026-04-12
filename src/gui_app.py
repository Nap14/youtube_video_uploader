from datetime import datetime
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import json
import csv
from src.automation import process_youtube_uploads, sync_to_lms
from src.report import create_report
from src.authenticated_service import Oauth2Service

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ZoomUploaderGUI(ctk.CTk):
    def __init__(self, config, schedule, paths):
        super().__init__()
        self.config = config
        self.schedule = schedule
        self.paths = paths
        
        self.title("Zoom Video Automation")
        self.geometry("1100x600")
        self.minsize(900, 500)
        
        # Grid layout for responsiveness
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Color mapping for courses (to use in calendar)
        self.course_colors = [
            ("#FF7675", "#D63031"), # Red/Coral
            ("#74B9FF", "#0984E3"), # Blue
            ("#55E6C1", "#58B19F"), # Mint
            ("#FAD390", "#F6B93B"), # Yellow/Orange
            ("#A29BFE", "#6C5CE7"), # Purple
            ("#FAB1A0", "#E17055"), # Peach
            ("#81ECEC", "#00CEC9"), # Cyan
        ]
        # Load Theme from config
        self.theme = self.config.get_data().get("THEME", "Dark")
        ctk.set_appearance_mode(self.theme)
        
        self.create_sidebar()
        self.appearance_mode_optionemenu.set(self.theme)
        
        self.create_dashboard_frame()
        self.create_settings_frame()
        self.create_schedule_frame()
        self.create_reports_frame()
        
        self.select_frame_by_name("dashboard")

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Zoom Uploader", font=ctk.CTkFont(size=20, weight="bold"), text_color=("gray10", "gray90"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.dash_button = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.select_frame_by_name("dashboard"), text_color=("gray10", "gray90"))
        self.dash_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="General Config", command=lambda: self.select_frame_by_name("settings"), text_color=("gray10", "gray90"))
        self.settings_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.schedule_button = ctk.CTkButton(self.sidebar_frame, text="Schedule Editor", command=lambda: self.select_frame_by_name("schedule"), text_color=("gray10", "gray90"))
        self.schedule_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.reports_button = ctk.CTkButton(self.sidebar_frame, text="Reports Viewer", command=lambda: self.select_frame_by_name("reports"), text_color=("gray10", "gray90"))
        self.reports_button.grid(row=4, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Theme:", anchor="w", text_color=("gray10", "gray90"))
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

    def create_dashboard_frame(self):
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.dashboard_frame.grid_columnconfigure(0, weight=1)
        self.dashboard_frame.grid_rowconfigure(4, weight=1)

        self.dash_label = ctk.CTkLabel(self.dashboard_frame, text="Automation Control", font=ctk.CTkFont(size=24, weight="bold"))
        self.dash_label.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")
        
        # Mode Selection
        self.mode_var = tk.StringVar(value="1")
        self.mode_frame = ctk.CTkFrame(self.dashboard_frame)
        self.mode_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        
        ctk.CTkRadioButton(self.mode_frame, text="Full Cycle (YT + LMS)", variable=self.mode_var, value="1").grid(row=0, column=0, padx=20, pady=10)
        ctk.CTkRadioButton(self.mode_frame, text="YouTube Only", variable=self.mode_var, value="2").grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkRadioButton(self.mode_frame, text="LMS Sync Only", variable=self.mode_var, value="3").grid(row=0, column=2, padx=20, pady=10)
        
        # Start Button - Centered
        self.btn_container = ctk.CTkFrame(self.dashboard_frame, fg_color="transparent")
        self.btn_container.grid(row=2, column=0, padx=30, pady=20, sticky="ew")
        self.btn_container.grid_columnconfigure(0, weight=1)
        
        self.start_btn = ctk.CTkButton(self.btn_container, text="START AUTOMATION", height=50, width=300, 
                                       command=self.start_task, font=ctk.CTkFont(size=14, weight="bold"))
        self.start_btn.grid(row=0, column=0)
        
        # Progress
        self.progress_bar = ctk.CTkProgressBar(self.dashboard_frame)
        self.progress_bar.grid(row=3, column=0, padx=30, pady=10, sticky="ew")
        self.progress_bar.set(0)
        
        # Log view
        self.log_text = ctk.CTkTextbox(self.dashboard_frame, height=250)
        self.log_text.grid(row=4, column=0, padx=30, pady=10, sticky="nsew")
        self.dashboard_frame.grid_rowconfigure(4, weight=1)

    def create_settings_frame(self):
        self.settings_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.settings_frame.grid_columnconfigure(0, weight=1)
        
        self.settings_label = ctk.CTkLabel(self.settings_frame, text="General Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.settings_label.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")
        
        # Fields for config.json (Unified Widths)
        ENTRY_WIDTH = 550
        
        # Zoom Dir with Browse
        self.zoom_dir_label = ctk.CTkLabel(self.settings_frame, text="Zoom Recordings Directory:")
        self.zoom_dir_label.grid(row=1, column=0, padx=30, pady=(10, 0), sticky="w")
        
        self.zoom_dir_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.zoom_dir_frame.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="w")
        
        self.zoom_dir_entry = ctk.CTkEntry(self.zoom_dir_frame, width=ENTRY_WIDTH)
        self.zoom_dir_entry.pack(side="left")
        self.zoom_dir_entry.insert(0, self.config.get_zoom_dir() or "")
        
        self.browse_btn = ctk.CTkButton(self.zoom_dir_frame, text="Browse", width=80, command=self.browse_zoom_dir)
        self.browse_btn.pack(side="left", padx=(10, 0))
        
        # LMS Token with Toggle
        self.lms_token_label = ctk.CTkLabel(self.settings_frame, text="LMS Bearer Token:")
        self.lms_token_label.grid(row=3, column=0, padx=30, pady=(10, 0), sticky="w")
        
        self.lms_token_frame = ctk.CTkFrame(self.settings_frame, fg_color="transparent")
        self.lms_token_frame.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="w")
        
        self.lms_token_entry = ctk.CTkEntry(self.lms_token_frame, width=ENTRY_WIDTH, show="*")
        self.lms_token_entry.pack(side="left")
        self.lms_token_entry.insert(0, self.config.get_lms_token() or "")
        
        self.show_token_var = tk.BooleanVar(value=False)
        self.show_token_btn = ctk.CTkCheckBox(self.lms_token_frame, text="Show", variable=self.show_token_var, 
                                              command=self.toggle_token_visibility, width=60)
        self.show_token_btn.pack(side="left", padx=(10, 0))

        self.school_id_label = ctk.CTkLabel(self.settings_frame, text="School ID:")
        self.school_id_label.grid(row=5, column=0, padx=30, pady=(10, 0), sticky="w")
        self.school_id_entry = ctk.CTkEntry(self.settings_frame, width=200)
        self.school_id_entry.grid(row=6, column=0, padx=30, pady=(0, 20), sticky="w")
        self.school_id_entry.insert(0, self.config.get_school_id() or "18828")

        self.save_settings_btn = ctk.CTkButton(self.settings_frame, text="Save Settings", command=self.save_general_settings, width=150)
        self.save_settings_btn.grid(row=7, column=0, padx=30, pady=20, sticky="w")

    def create_schedule_frame(self):
        self.schedule_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.schedule_frame.grid_columnconfigure(0, weight=1)
        self.schedule_frame.grid_rowconfigure(1, weight=1)
        
        header_frame = ctk.CTkFrame(self.schedule_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(30, 20))
        
        self.schedule_label = ctk.CTkLabel(header_frame, text="Weekly Schedule", font=ctk.CTkFont(size=24, weight="bold"))
        self.schedule_label.pack(side="left")
        
        self.add_lesson_btn = ctk.CTkButton(header_frame, text="+ Add Lesson", width=120, command=self.open_edit_modal)
        self.add_lesson_btn.pack(side="right")

        # Calendar View Container
        self.calendar_container = ctk.CTkScrollableFrame(self.schedule_frame)
        self.calendar_container.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.calendar_container.grid_columnconfigure(list(range(1, 8)), weight=1) # 7 columns for days
        
        self.populate_schedule_view()

    def get_course_color(self, name):
        import hashlib
        # Normalize name to ensure "Course A" and "course a  " have the same color
        normalized = name.strip().lower()
        h = int(hashlib.md5(normalized.encode()).hexdigest(), 16)
        return self.course_colors[h % len(self.course_colors)]

    def populate_schedule_view(self):
        # Clear existing
        for child in self.calendar_container.winfo_children():
            child.destroy()
            
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ua_days = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "НД"]
        
        # Header - Day Names
        for i, day_name in enumerate(ua_days):
            lbl = ctk.CTkLabel(self.calendar_container, text=day_name, font=ctk.CTkFont(weight="bold"))
            lbl.grid(row=0, column=i+1, pady=10, sticky="ew")

        # Background Grid (Hourly)
        for row in range(1, 16):
             hour = 7 + row
             lbl = ctk.CTkLabel(self.calendar_container, text=f"{hour}:00", font=ctk.CTkFont(size=10), text_color="gray60")
             lbl.grid(row=row, column=0, padx=(0, 10), sticky="ne")
             
             for col in range(1, 8):
                 btn = ctk.CTkButton(self.calendar_container, text="", fg_color="transparent", 
                                      border_width=1, border_color=("gray95", "gray25"), 
                                      hover_color=("gray85", "gray35"), corner_radius=0, height=50,
                                      command=lambda d=days[col-1], t=f"{hour}:00": self.open_edit_modal(d, t))
                 btn.grid(row=row, column=col, sticky="nsew")

        # Populate lessons
        for day_idx, day_name in enumerate(days):
            day_data = self.schedule.get(day_name, {})
            for time_str, data in day_data.items():
                try:
                    h, m = map(int, time_str.split(':'))
                    row_idx = (h - 7)
                    if row_idx < 1: continue
                    
                    name = data if isinstance(data, str) else data.get("name", "Unnamed")
                    duration = 60 if isinstance(data, str) else int(data.get("duration", 60))
                    row_span = max(1, duration // 60)
                    
                    color_light, color_dark = self.get_course_color(name)
                    
                    wrapped_name = name
                    if len(name) > 12:
                        parts = [name[i:i+12] for i in range(0, len(name), 12)]
                        wrapped_name = "\n".join(parts)

                    lesson_btn = ctk.CTkButton(self.calendar_container, text=wrapped_name, 
                                              fg_color=(color_light, color_dark),
                                              text_color="white",
                                              font=ctk.CTkFont(size=10, weight="bold"),
                                              corner_radius=4,
                                              height=48 * row_span,
                                              command=lambda d=day_name, t=time_str, v=data: self.open_edit_modal(d, t, v))
                    lesson_btn.grid(row=row_idx, column=day_idx+1, rowspan=row_span, padx=2, pady=2, sticky="nsew")
                except:
                    continue
        self.calendar_container.update_idletasks()

    def open_edit_modal(self, day=None, time=None, value=None):
        modal = ctk.CTkToplevel(self)
        modal.title("Edit Lesson" if day and time and value else "Add New Lesson")
        modal.geometry("700x520")
        modal.resizable(True, True)
        # Ensure it's handled like a proper sub-window
        modal.transient(self)
        modal.grab_set()
        modal.focus_set()
        
        modal.grid_columnconfigure((0, 1), weight=1)
        
        # Day (Mandatory *)
        day_label_frame = ctk.CTkFrame(modal, fg_color="transparent")
        day_label_frame.grid(row=0, column=0, padx=20, pady=(20, 0), sticky="w")
        ctk.CTkLabel(day_label_frame, text="Day").pack(side="left")
        ctk.CTkLabel(day_label_frame, text="*", text_color="red").pack(side="left")
        
        day_cb = ctk.CTkComboBox(modal, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], width=250)
        day_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        if day: day_cb.set(day)
        
        # Time (Mandatory *) - Restore ComboBox Picker
        time_label_frame = ctk.CTkFrame(modal, fg_color="transparent")
        time_label_frame.grid(row=0, column=1, padx=20, pady=(20, 0), sticky="w")
        ctk.CTkLabel(time_label_frame, text="Time").pack(side="left")
        ctk.CTkLabel(time_label_frame, text="*", text_color="red").pack(side="left")
        
        time_frame = ctk.CTkFrame(modal, fg_color="transparent")
        time_frame.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        hour_cb = ctk.CTkComboBox(time_frame, values=[f"{i:02d}" for i in range(8, 23)], width=100)
        hour_cb.pack(side="left")
        ctk.CTkLabel(time_frame, text=" : ").pack(side="left")
        min_cb = ctk.CTkComboBox(time_frame, values=["00", "15", "30", "45"], width=100)
        min_cb.pack(side="left")
        
        if time:
            h, m = time.split(':')
            hour_cb.set(h)
            min_cb.set(m if m in ["00", "15", "30", "45"] else "00")
        
        # Course Name (Mandatory *)
        name_label_frame = ctk.CTkFrame(modal, fg_color="transparent")
        name_label_frame.grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        ctk.CTkLabel(name_label_frame, text="Course Name").pack(side="left")
        ctk.CTkLabel(name_label_frame, text="*", text_color="red").pack(side="left")
        
        name_entry = ctk.CTkEntry(modal, width=300)
        name_entry.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        if value: 
            name = value if isinstance(value, str) else value.get("name", "")
            name_entry.insert(0, name)

        # LMS ID
        ctk.CTkLabel(modal, text="LMS Course ID:").grid(row=2, column=1, padx=20, pady=(10, 0), sticky="w")
        lms_id_entry = ctk.CTkEntry(modal, width=300)
        lms_id_entry.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        if value and isinstance(value, dict):
            lms_id_entry.insert(0, value.get("lms_course_id", ""))

        # Image (Thumbnail)
        ctk.CTkLabel(modal, text="Course Image / Thumbnail:").grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        img_frame = ctk.CTkFrame(modal, fg_color="transparent")
        img_frame.grid(row=5, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        img_entry = ctk.CTkEntry(img_frame, width=500)
        img_entry.pack(side="left", fill="x", expand=True)
        if value and isinstance(value, dict):
            thumb = value.get("thumbnail") or value.get("image", "")
            img_entry.insert(0, thumb)
            
        def browse_img():
            f = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp")])
            if f:
                img_entry.delete(0, "end")
                img_entry.insert(0, f)
        
        ctk.CTkButton(img_frame, text="Browse", width=80, command=browse_img).pack(side="left", padx=(10, 0))

        # Duration
        ctk.CTkLabel(modal, text="Duration (minutes):").grid(row=6, column=0, padx=20, pady=(10, 0), sticky="w")
        duration_entry = ctk.CTkEntry(modal, width=100)
        duration_entry.grid(row=7, column=0, padx=20, pady=5, sticky="w")
        duration_entry.insert(0, "60" if not value or isinstance(value, str) else str(value.get("duration", 60)))

        # Buttons (Restore side-by-side layout)
        btn_frame = ctk.CTkFrame(modal, fg_color="transparent")
        btn_frame.grid(row=8, column=0, columnspan=2, padx=20, pady=40, sticky="ew")
        
        def save():
            d = day_cb.get()
            h = hour_cb.get()
            m = min_cb.get()
            t = f"{h}:{m}"
            name = name_entry.get().strip()
            
            # STRICT VALIDATION
            if not d or not h or not m or not name:
                messagebox.showwarning("Validation Error", "Please fill all mandatory fields (*):\n- Day\n- Time\n- Course Name")
                return
            
            old_data = value if isinstance(value, dict) else {}
            new_data = old_data.copy()
            
            new_data.update({
                "name": name,
                "lms_course_id": lms_id_entry.get(),
                "duration": int(duration_entry.get() if duration_entry.get().isdigit() else 60),
                "thumbnail": img_entry.get()
            })
            if "image" in new_data: del new_data["image"]
            
            # If day/time changed, or new lesson, update
            if d not in self.schedule: self.schedule[d] = {}
            self.schedule[d][t] = new_data
            
            # SAFE CHECK: Only delete old if it actually exists (fixes KeyError)
            if day and time and day in self.schedule and time in self.schedule[day] and (d != day or t != time):
                del self.schedule[day][time]
            
            self.save_schedule_to_file()
            self.populate_schedule_view()
            modal.destroy()

        def delete():
            if day and time and day in self.schedule and time in self.schedule[day]:
                if messagebox.askyesno("Confirm", f"Delete lesson at {time} on {day}?"):
                    del self.schedule[day][time]
                    self.save_schedule_to_file()
                    self.populate_schedule_view()
                    modal.destroy()

        # Restore layout: Save/Delete left, Cancel right
        ctk.CTkButton(btn_frame, text="Save", command=save, width=120, fg_color="#27ae60").pack(side="left", padx=5)
        if day and time and value:
            ctk.CTkButton(btn_frame, text="Delete", fg_color="#e74c3c", command=delete, width=120).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", fg_color="gray", command=modal.destroy, width=120).pack(side="right", padx=5)



    def save_schedule_to_file(self):
        try:
            with open(self.paths['SCHEDULE_FILE'], 'w', encoding='utf-8') as f:
                json.dump(self.schedule, f, indent=4, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save schedule: {e}")

    def create_reports_frame(self):
        self.reports_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.reports_frame.grid_columnconfigure(0, weight=1)
        self.reports_frame.grid_rowconfigure(2, weight=1)
        
        self.reports_label = ctk.CTkLabel(self.reports_frame, text="Reports History", font=ctk.CTkFont(size=24, weight="bold"))
        self.reports_label.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")
        
        self.refresh_reports_btn = ctk.CTkButton(self.reports_frame, text="Refresh List", command=self.refresh_reports)
        self.refresh_reports_btn.grid(row=1, column=0, padx=30, pady=10, sticky="w")
        
        self.reports_list = ctk.CTkTextbox(self.reports_frame, height=400)
        self.reports_list.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="nsew")
        
        self.refresh_reports()

    def select_frame_by_name(self, name):
        # Reset buttons
        self.dash_button.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")
        self.schedule_button.configure(fg_color=("gray75", "gray25") if name == "schedule" else "transparent")
        self.reports_button.configure(fg_color=("gray75", "gray25") if name == "reports" else "transparent")

        # Show frame
        if name == "dashboard": self.dashboard_frame.grid(row=0, column=1, sticky="nsew")
        else: self.dashboard_frame.grid_forget()
        if name == "settings": self.settings_frame.grid(row=0, column=1, sticky="nsew")
        else: self.settings_frame.grid_forget()
        if name == "schedule": self.schedule_frame.grid(row=0, column=1, sticky="nsew")
        else: self.schedule_frame.grid_forget()
        if name == "reports": self.reports_frame.grid(row=0, column=1, sticky="nsew")
        else: self.reports_frame.grid_forget()

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)
        # Save to config via internal method
        self.config.get_data()["THEME"] = new_appearance_mode
        self.config.save()

    def browse_zoom_dir(self):
        directory = filedialog.askdirectory(initialdir=self.zoom_dir_entry.get())
        if directory:
            self.zoom_dir_entry.delete(0, "end")
            self.zoom_dir_entry.insert(0, directory)

    def toggle_token_visibility(self):
        if self.show_token_var.get():
            self.lms_token_entry.configure(show="")
        else:
            self.lms_token_entry.configure(show="*")

    # --- Logic ---

    def log(self, message, is_detail=False):
        """
        is_detail: if True, the message is a secondary step.
        """
        if not is_detail:
            # If it's a new main step, we could optionally clear previous details
            # but for now we just label it clearly.
            prefix = "• "
        else:
            prefix = "  > "
            
        self.log_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} {prefix}{message}\n")
        self.log_text.see("end")

    def clear_logs(self):
        self.log_text.delete("1.0", "end")

    def update_progress(self, message, progress):
        curr, total = progress
        self.progress_bar.set(curr / total if total > 0 else 0)
        self.log(message)
        
        # If a major step is starting (e.g. 0% of a phase), we can add a separator
        if curr == 0:
            self.log("-" * 40, is_detail=True)

    def start_task(self):
        mode = self.mode_var.get()
        self.start_btn.configure(state="disabled")
        self.log_text.delete("1.0", "end")
        self.log(f"Starting Task in Mode {mode}...")
        
        threading.Thread(target=self.run_automation, args=(mode,), daemon=True).start()

    def run_automation(self, mode):
        try:
            reports_dir = self.config.get_reports_dir()
            
            if mode in ['1', '2']:
                if not os.path.exists(self.paths['CLIENT_SECRETS_FILE']):
                    self.log("ERROR: client_secret.json missing in configs/")
                    self.start_btn.configure(state="normal")
                    return
                
                oauth2 = Oauth2Service(self.custom_logger())
                youtube = oauth2.get_youtube_service(self.paths['TOKEN_FILE'], self.paths['CLIENT_SECRETS_FILE'])
                
                rows = process_youtube_uploads(self.config, self.schedule, youtube, status_callback=self.update_progress)
                
                if rows:
                    report_path = create_report(reports_dir, rows, "youtube")
                    self.log(f"YouTube report saved: {report_path}")
                    
                    if mode == '1':
                        self.log("Starting LMS Sync...")
                        lms_rows = sync_to_lms(rows, self.config, self.schedule, status_callback=self.update_progress)
                        if lms_rows:
                            lms_path = create_report(reports_dir, lms_rows, "lms")
                            self.log(f"LMS report saved: {lms_path}")
                else:
                    self.log("No videos found to upload.")

            elif mode == '3':
                report_file = filedialog.askopenfilename(
                    initialdir=reports_dir,
                    title="Select YouTube Report CSV",
                    filetypes=(("CSV files", "*.csv"), ("all files", "*.*"))
                )
                if not report_file:
                    self.log("LMS Sync cancelled.")
                else:
                    rows = []
                    with open(report_file, 'r', encoding='utf-8') as f:
                        reader = csv.reader(f)
                        next(reader)
                        for r in reader: rows.append(r)
                    
                    lms_rows = sync_to_lms(rows, self.config, self.schedule, status_callback=self.update_progress)
                    if lms_rows:
                        lms_path = create_report(reports_dir, lms_rows, "lms")
                        self.log(f"LMS Sync complete: {lms_path}")

        except Exception as e:
            self.log(f"FATAL ERROR: {str(e)}")
        
        self.log("Done.")
        self.start_btn.configure(state="normal")
        self.refresh_reports()

    def custom_logger(self):
        # Redirect all console-like logs to our GUI log as "detail"
        class GuiLogger:
            def __init__(self, parent): self.parent = parent
            def info(self, m): self.parent.log(m, is_detail=True)
            def error(self, m): self.parent.log(f"ERROR: {m}", is_detail=True)
            def warning(self, m): self.parent.log(f"WARN: {m}", is_detail=True)
            def critical(self, m): self.parent.log(f"CRIT: {m}", is_detail=True)
        return GuiLogger(self)

    def save_general_settings(self):
        data = self.config.get_data()
        data.update({
            "ZOOM_DIR": self.zoom_dir_entry.get(),
            "LMS_TOKEN": self.lms_token_entry.get(),
            "SCHOOL_ID": self.school_id_entry.get(),
            "REPORTS_DIR": self.config.get_reports_dir()
        })
        try:
            self.config.save()
            messagebox.showinfo("Success", "General settings saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")

    def save_schedule_json(self):
        text = self.schedule_text.get("1.0", "end-1c")
        try:
            # Validate JSON
            data = json.loads(text)
            with open(self.paths['SCHEDULE_FILE'], 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Success", "Schedule updated successfully.")
        except Exception as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format: {e}")

    def refresh_reports(self):
        reports_dir = self.config.get_reports_dir()
        self.reports_list.delete("1.0", "end")
        if not os.path.exists(reports_dir): return
        
        files = sorted(os.listdir(reports_dir), reverse=True)
        for f in files:
            if f.endswith(('.txt', '.csv')):
                self.reports_list.insert("end", f"{f}\n")
