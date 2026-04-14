import os
import csv
import customtkinter as ctk
from tkinter import filedialog

from src.core.context import AppContext
from src.gui.base_frame import BaseFrame
from src.services.report_utils import get_latest_report
from src.services.ui_service import UIService
from .viewer import ReportTableModal

class DashboardFrame(BaseFrame):
    def __init__(self, master, ctx: AppContext, start_cmd, **kwargs):
        self.start_command = start_cmd
        super().__init__(master, ctx, **kwargs)
        self.mode_var.trace_add("write", self._on_mode_change)

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self._init_header()
        self._init_mode_selection()
        self._init_lms_file_section()
        self._init_controls()
        self._init_logs()

    def _init_header(self):
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=0, column=0, padx=30, pady=(30, 10), sticky="ew")
        
        ctk.CTkLabel(h, text="Automation Control", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.rep_btn = ctk.CTkButton(
            h, text="Latest Report", fg_color="#34495e", command=self._open_latest
        )
        self.rep_btn.pack(side="right", padx=10)

    def _init_mode_selection(self):
        self.mode_var = ctk.StringVar(value="1")
        mf = ctk.CTkFrame(self, fg_color="transparent")
        mf.grid(row=1, column=0, padx=30, pady=10, sticky="w")
        
        modes = [("Full Auto", "1"), ("YT Only", "2"), ("LMS Only", "3")]
        for i, (t, v) in enumerate(modes):
            ctk.CTkRadioButton(mf, text=t, variable=self.mode_var, value=v).grid(row=0, column=i, padx=20)

    def _init_lms_file_section(self):
        self.lms_f = ctk.CTkFrame(self, fg_color=("gray90", "gray20"))
        self.lms_ent = ctk.CTkEntry(self.lms_f, width=400, placeholder_text="Select YouTube CSV...")
        self.lms_ent.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            self.lms_f, text="Browse", width=80, command=self._browse_lms
        ).pack(side="left", padx=(0,10))

    def _init_controls(self):
        self.start_btn = ctk.CTkButton(
            self, text="START AUTOMATION", height=45, width=250, 
            command=self.start_command, font=ctk.CTkFont(weight="bold")
        )
        self.start_btn.grid(row=3, column=0, pady=10)
        
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.grid(row=4, column=0, padx=30, pady=5, sticky="ew")
        self.progress_bar.set(0)

    def _init_logs(self):
        lt_h = ctk.CTkFrame(self, fg_color="transparent")
        lt_h.grid(row=5, column=0, padx=30, pady=(10, 0), sticky="ew")
        
        ctk.CTkLabel(lt_h, text="Console Log", font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        ctk.CTkButton(lt_h, text="Clear", width=50, fg_color="gray", command=self.clear_logs).pack(side="right")
        
        self.log_text = ctk.CTkTextbox(self, height=200, state="disabled")
        self.log_text.grid(row=6, column=0, padx=30, pady=(0, 20), sticky="nsew")
        self.grid_rowconfigure(6, weight=1)

    def _browse_lms(self):
        f = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if not f:
            return
            
        try:
            with open(f, 'r', encoding='utf-8') as file:
                if not list(csv.reader(file)):
                    raise ValueError("Empty")
                    
            self.lms_ent.delete(0, "end")
            self.lms_ent.insert(0, f)
            self.start_btn.configure(state="normal")
        except Exception as e:
            UIService.error("Error", f"Invalid file: {e}")

    def _on_mode_change(self, *args):
        if self.mode_var.get() == "3":
            self.lms_f.grid(row=2, column=0, padx=30, pady=10, sticky="w")
        else:
            self.lms_f.grid_forget()
            
        is_lms_ready = self.mode_var.get() == "3" and not self.lms_ent.get()
        state = "disabled" if is_lms_ready else "normal"
        self.start_btn.configure(state=state)

    def refresh(self):
        lat = get_latest_report(self.ctx.config.get_reports_dir())
        
        btn_text = os.path.basename(lat) if lat else "No reports"
        btn_state = "normal" if lat else "disabled"
        
        self.rep_btn.configure(text=btn_text, state=btn_state)
        self._latest_path = lat

    def _open_latest(self):
        if hasattr(self, "_latest_path") and self._latest_path:
            ReportTableModal(self.master, self._latest_path)

    def clear_logs(self):
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", "end")
        self.log_text.configure(state="disabled")
