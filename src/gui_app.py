import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import logging
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
        self.paths = paths # dict with file paths
        
        self.title("Zoom Video Automation")
        self.geometry("1100x600")
        
        # Grid layout 1x2 (Sidebar + Content)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.create_sidebar()
        self.create_dashboard_frame()
        self.create_settings_frame()
        self.create_schedule_frame()
        self.create_reports_frame()
        
        self.select_frame_by_name("dashboard")

    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Zoom Uploader", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.dash_button = ctk.CTkButton(self.sidebar_frame, text="Dashboard", command=lambda: self.select_frame_by_name("dashboard"))
        self.dash_button.grid(row=1, column=0, padx=20, pady=10)
        
        self.settings_button = ctk.CTkButton(self.sidebar_frame, text="General Config", command=lambda: self.select_frame_by_name("settings"))
        self.settings_button.grid(row=2, column=0, padx=20, pady=10)
        
        self.schedule_button = ctk.CTkButton(self.sidebar_frame, text="Schedule Editor", command=lambda: self.select_frame_by_name("schedule"))
        self.schedule_button.grid(row=3, column=0, padx=20, pady=10)
        
        self.reports_button = ctk.CTkButton(self.sidebar_frame, text="Reports Viewer", command=lambda: self.select_frame_by_name("reports"))
        self.reports_button.grid(row=4, column=0, padx=20, pady=10)
        
        self.appearance_mode_label = ctk.CTkLabel(self.sidebar_frame, text="Theme:", anchor="w")
        self.appearance_mode_label.grid(row=6, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"], command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=7, column=0, padx=20, pady=(10, 20))

    def create_dashboard_frame(self):
        self.dashboard_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        
        self.dash_label = ctk.CTkLabel(self.dashboard_frame, text="Automation Control", font=ctk.CTkFont(size=24, weight="bold"))
        self.dash_label.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")
        
        # Mode Selection
        self.mode_var = tk.StringVar(value="1")
        self.mode_frame = ctk.CTkFrame(self.dashboard_frame)
        self.mode_frame.grid(row=1, column=0, padx=30, pady=10, sticky="ew")
        
        ctk.CTkRadioButton(self.mode_frame, text="Full Cycle (YT + LMS)", variable=self.mode_var, value="1").grid(row=0, column=0, padx=20, pady=10)
        ctk.CTkRadioButton(self.mode_frame, text="YouTube Only", variable=self.mode_var, value="2").grid(row=0, column=1, padx=20, pady=10)
        ctk.CTkRadioButton(self.mode_frame, text="LMS Sync Only", variable=self.mode_var, value="3").grid(row=0, column=2, padx=20, pady=10)
        
        # Start Button
        self.start_btn = ctk.CTkButton(self.dashboard_frame, text="START AUTOMATION", height=50, command=self.start_task, font=ctk.CTkFont(weight="bold"))
        self.start_btn.grid(row=2, column=0, padx=30, pady=20, sticky="ew")
        
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
        self.settings_label = ctk.CTkLabel(self.settings_frame, text="General Settings", font=ctk.CTkFont(size=24, weight="bold"))
        self.settings_label.grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")
        
        # Fields for config.json
        self.zoom_dir_label = ctk.CTkLabel(self.settings_frame, text="Zoom Recordings Directory:")
        self.zoom_dir_label.grid(row=1, column=0, padx=30, pady=(10, 0), sticky="w")
        
        self.zoom_dir_entry = ctk.CTkEntry(self.settings_frame, width=600)
        self.zoom_dir_entry.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="w")
        self.zoom_dir_entry.insert(0, self.config.get_zoom_dir() or "")
        
        self.lms_token_label = ctk.CTkLabel(self.settings_frame, text="LMS Bearer Token:")
        self.lms_token_label.grid(row=3, column=0, padx=30, pady=(10, 0), sticky="w")
        self.lms_token_entry = ctk.CTkEntry(self.settings_frame, width=600)
        self.lms_token_entry.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="w")
        self.lms_token_entry.insert(0, self.config.get_lms_token() or "")

        self.school_id_label = ctk.CTkLabel(self.settings_frame, text="School ID:")
        self.school_id_label.grid(row=5, column=0, padx=30, pady=(10, 0), sticky="w")
        self.school_id_entry = ctk.CTkEntry(self.settings_frame, width=200)
        self.school_id_entry.grid(row=6, column=0, padx=30, pady=(0, 20), sticky="w")
        self.school_id_entry.insert(0, self.config.get_school_id() or "18828")

        self.save_settings_btn = ctk.CTkButton(self.settings_frame, text="Save Settings", command=self.save_general_settings)
        self.save_settings_btn.grid(row=7, column=0, padx=30, pady=20, sticky="w")

    def create_schedule_frame(self):
        self.schedule_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.schedule_label = ctk.CTkLabel(self.schedule_frame, text="Schedule Editor (JSON)", font=ctk.CTkFont(size=24, weight="bold"))
        self.schedule_label.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")
        
        self.schedule_info = ctk.CTkLabel(self.schedule_frame, text="Edit your schedule.json below. Be careful with commas and brackets!")
        self.schedule_info.grid(row=1, column=0, padx=30, pady=0, sticky="w")
        
        self.schedule_text = ctk.CTkTextbox(self.schedule_frame, height=400, width=800)
        self.schedule_text.grid(row=2, column=0, padx=30, pady=20, sticky="nsew")
        self.schedule_frame.grid_rowconfigure(2, weight=1)
        
        # Load schedule into text
        try:
            with open(self.paths['SCHEDULE_FILE'], 'r', encoding='utf-8') as f:
                self.schedule_text.insert("1.0", f.read())
        except:
             pass
             
        self.save_schedule_btn = ctk.CTkButton(self.schedule_frame, text="Update Schedule", command=self.save_schedule_json)
        self.save_schedule_btn.grid(row=3, column=0, padx=30, pady=10, sticky="w")

    def create_reports_frame(self):
        self.reports_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.reports_label = ctk.CTkLabel(self.reports_frame, text="Reports History", font=ctk.CTkFont(size=24, weight="bold"))
        self.reports_label.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")
        
        self.refresh_reports_btn = ctk.CTkButton(self.reports_frame, text="Refresh List", command=self.refresh_reports)
        self.refresh_reports_btn.grid(row=1, column=0, padx=30, pady=10, sticky="w")
        
        self.reports_list = ctk.CTkTextbox(self.reports_frame, height=400, width=800)
        self.reports_list.grid(row=2, column=0, padx=30, pady=0, sticky="nsew")
        self.reports_frame.grid_rowconfigure(2, weight=1)
        
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

    # --- Logic ---

    def log(self, message):
        self.log_text.insert("end", f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see("end")

    def update_progress(self, message, progress):
        curr, total = progress
        self.progress_bar.set(curr / total if total > 0 else 0)
        self.log(message)

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
        # Dummy logger that redirects to self.log
        class GuiLogger:
            def __init__(self, parent): self.parent = parent
            def info(self, m): self.parent.log(f"[INFO] {m}")
            def error(self, m): self.parent.log(f"[ERROR] {m}")
            def warning(self, m): self.parent.log(f"[WARN] {m}")
            def critical(self, m): self.parent.log(f"[CRIT] {m}")
        return GuiLogger(self)

    def save_general_settings(self):
        new_config = {
            "ZOOM_DIR": self.zoom_dir_entry.get(),
            "LMS_TOKEN": self.lms_token_entry.get(),
            "SCHOOL_ID": self.school_id_entry.get(),
            "REPORTS_DIR": self.config.get_reports_dir()
        }
        try:
            with open(self.paths['CONFIG_FILE'], 'w', encoding='utf-8') as f:
                json.dump(new_config, f, indent=4)
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
