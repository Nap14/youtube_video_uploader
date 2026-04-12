import customtkinter as ctk
import os

from .viewer import ReportTableModal

class ReportsFrame(ctk.CTkFrame):
    def __init__(self, master, config, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Reports Management", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, columnspan=2, padx=30, pady=(30, 10), sticky="w")
        
        btn_f = ctk.CTkFrame(self, fg_color="transparent")
        btn_f.grid(row=1, column=0, columnspan=2, padx=30, pady=10, sticky="w")
        ctk.CTkButton(btn_f, text="Refresh All", command=self.refresh_reports, width=120).pack(side="left")
        ctk.CTkButton(btn_f, text="Clear All History", fg_color="#e74c3c", command=self.clear_all, width=150).pack(side="left", padx=10)
        
        # Youtube Column
        ctk.CTkLabel(self, text="YouTube Reports", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=30, pady=(10,0), sticky="w")
        self.yt_list = ctk.CTkScrollableFrame(self)
        self.yt_list.grid(row=3, column=0, padx=(30, 10), pady=10, sticky="nsew")
        
        # LMS Column
        ctk.CTkLabel(self, text="LMS Reports", font=ctk.CTkFont(weight="bold")).grid(row=2, column=1, padx=30, pady=(10,0), sticky="w")
        self.lms_list = ctk.CTkScrollableFrame(self)
        self.lms_list.grid(row=3, column=1, padx=(10, 30), pady=10, sticky="nsew")

    def refresh_reports(self):
        for c in self.yt_list.winfo_children(): c.destroy()
        for c in self.lms_list.winfo_children(): c.destroy()
        
        d = self.config.get_reports_dir()
        if not os.path.exists(d): return
        
        files = os.listdir(d)
        files.sort(key=lambda x: os.path.getmtime(os.path.join(d, x)), reverse=True)
        
        for f in files:
            target = self.yt_list if "youtube" in f.lower() else self.lms_list if "lms" in f.lower() else None
            if target: self._add_report_row(target, f, os.path.join(d, f))

    def _add_report_row(self, container, filename, full_path):
        row = ctk.CTkFrame(container, fg_color=("gray90", "gray20"))
        row.pack(fill="x", padx=5, pady=2)
        
        ctk.CTkLabel(row, text=filename, font=ctk.CTkFont(size=11), anchor="w").pack(side="left", padx=10, fill="x", expand=True)
        
        if filename.endswith(".csv"):
            ctk.CTkButton(row, text="View", width=50, height=22, command=lambda p=full_path: ReportTableModal(self, p)).pack(side="left", padx=2)
        else:
            ctk.CTkButton(row, text="Open", width=50, height=22, fg_color="gray", command=lambda p=full_path: os.startfile(p)).pack(side="left", padx=2)
            
        ctk.CTkButton(row, text="X", width=25, height=22, fg_color="#e74c3c", command=lambda p=full_path: self.delete_report(p)).pack(side="right", padx=5)

    def delete_report(self, path):
        from tkinter import messagebox
        if messagebox.askyesno("Confirm", "Delete this report?"):
            os.remove(path)
            # Remove the .txt version too if it exists
            if path.endswith(".csv"):
                txt = path.replace(".csv", ".txt")
                if os.path.exists(txt): os.remove(txt)
            self.refresh_reports()

    def clear_all(self):
        from tkinter import messagebox
        if messagebox.askyesno("Confirm", "Delete ALL reports?"):
            d = self.config.get_reports_dir()
            for f in os.listdir(d): os.remove(os.path.join(d, f))
            self.refresh_reports()
