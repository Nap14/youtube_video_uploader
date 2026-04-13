import os
import customtkinter as ctk
from ..services.report_utils import get_latest_report

class DashboardFrame(ctk.CTkFrame):
    def __init__(self, master, config, start_cmd, browse_lms_cmd, view_report_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self.config, self.start_command = config, start_cmd
        self.browse_lms_cmd, self.view_report_cmd = browse_lms_cmd, view_report_cmd
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(6, weight=1)
        self.create_widgets()
        self.mode_var.trace_add("write", self._on_mode_change)

    def create_widgets(self):
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        ctk.CTkLabel(h, text="Automation Control", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        self.report_link = ctk.CTkButton(h, text="Latest Report", width=140, height=28, 
                                         fg_color="#34495e", command=self._open_latest)
        self.report_link.pack(side="right", padx=10)
        
        self.mode_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.mode_frame.grid(row=1, column=0, padx=30, pady=10, sticky="w")
        self.mode_var = ctk.StringVar(value="1")
        modes = [("Full Auto", "1"), ("YouTube Only", "2"), ("LMS Sync Only", "3")]
        for i, (text, val) in enumerate(modes):
            ctk.CTkRadioButton(self.mode_frame, text=text, variable=self.mode_var, value=val).grid(row=0, column=i, padx=20)

        self.lms_file_frame = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        self.lms_file_entry = ctk.CTkEntry(self.lms_file_frame, width=400, placeholder_text="Select YouTube CSV for LMS sync...")
        self.lms_file_entry.pack(side="left", padx=10, pady=10)
        ctk.CTkButton(self.lms_file_frame, text="Browse", width=80, command=self.browse_lms_cmd).pack(side="left", padx=(0,10))

        self.btn_container = ctk.CTkFrame(self, fg_color="transparent")
        self.btn_container.grid(row=3, column=0, padx=30, pady=10, sticky="ew")
        self.start_btn = ctk.CTkButton(self.btn_container, text="START AUTOMATION", height=45, width=250, 
                                       command=self.start_command, font=ctk.CTkFont(size=14, weight="bold"))
        self.start_btn.pack(side="top", pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, padx=30, pady=5, sticky="ew")
        self.progress_bar.set(0)
        
        log_h = ctk.CTkFrame(self, fg_color="transparent")
        log_h.grid(row=5, column=0, padx=30, pady=(10, 0), sticky="ew")
        ctk.CTkLabel(log_h, text="Console Log", font=ctk.CTkFont(weight="bold")).pack(side="left")
        ctk.CTkButton(log_h, text="Clear", width=50, height=20, fg_color="gray", command=self.clear_logs).pack(side="right")

        self.log_text = ctk.CTkTextbox(self, height=200, state="disabled")
        self.log_text.grid(row=6, column=0, padx=30, pady=(0, 20), sticky="nsew")

    def update_start_state(self):
        if self.mode_var.get() == "3" and not self.lms_file_entry.get():
            self.start_btn.configure(state="disabled")
        else:
            self.start_btn.configure(state="normal")

    def _on_mode_change(self, *args):
        if self.mode_var.get() == "3":
            self.lms_file_frame.grid(row=2, column=0, padx=30, pady=10, sticky="w")
        else:
            self.lms_file_frame.grid_forget()
        self.update_start_state()

    def refresh(self):
        latest = get_latest_report(self.config.get_reports_dir())
        if latest:
            self.report_link.configure(text=os.path.basename(latest), state="normal")
            self._latest_path = latest
        else:
            self.report_link.configure(text="No reports", state="disabled")

    def _open_latest(self):
        if hasattr(self, "_latest_path"): 
            self.view_report_cmd(self._latest_path)

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
