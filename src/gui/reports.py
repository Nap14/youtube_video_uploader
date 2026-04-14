import os
import customtkinter as ctk
from tkinter import messagebox

from .viewer import ReportTableModal
from .base_frame import BaseFrame
from ..services.report_utils import list_reports

class ReportsFrame(BaseFrame):
    def __init__(self, master, ctx, **kwargs):
        super().__init__(master, ctx, **kwargs)

    def _create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(3, weight=1)
        
        title_font = ctk.CTkFont(size=24, weight="bold")
        ctk.CTkLabel(self, text="Reports Management", font=title_font).grid(
            row=0, column=0, columnspan=2, padx=30, pady=(20, 5), sticky="w"
        )
        
        self._init_top_buttons()
        self._init_lists()

    def _init_top_buttons(self):
        btn_f = ctk.CTkFrame(self, fg_color="transparent")
        btn_f.grid(row=1, column=0, columnspan=2, padx=30, pady=10, sticky="w")
        
        ctk.CTkButton(btn_f, text="Refresh All", command=self.refresh, width=120).pack(side="left")
        ctk.CTkButton(
            btn_f, text="Clear All History", fg_color="#e74c3c", 
            command=self.clear_all, width=150
        ).pack(side="left", padx=10)

    def _init_lists(self):
        self._init_list_section("YouTube Reports", "youtube", 0)
        self._init_list_section("LMS Reports", "lms", 1)

    def _init_list_section(self, title, prefix, col):
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=2, column=col, padx=30, pady=(10, 0), sticky="ew")
        
        ctk.CTkLabel(h, text=title, font=ctk.CTkFont(weight="bold")).pack(side="left")
        
        cb = lambda: self.clear_partial(prefix)
        ctk.CTkButton(
            h, text="Clear", width=50, height=20, fg_color="#e67e22", command=cb
        ).pack(side="right")
        
        scroll = ctk.CTkScrollableFrame(self)
        scroll.grid(row=3, column=col, padx=20, pady=10, sticky="nsew")
        
        if prefix == "youtube":
            self.yt_list = scroll
        else:
            self.lms_list = scroll

    def refresh(self):
        for c in self.yt_list.winfo_children():
            c.destroy()
        for c in self.lms_list.winfo_children():
            c.destroy()
        
        d = self.ctx.config.get_reports_dir()
        files = list_reports(d)
        
        for f in files:
            target = None
            if "youtube" in f.lower():
                target = self.yt_list
            elif "lms" in f.lower():
                target = self.lms_list
                
            if target:
                self._add_report_row(target, f, os.path.join(d, f))

    def _add_report_row(self, container, filename, full_path):
        row = ctk.CTkFrame(container, fg_color=("gray90", "gray20"))
        row.pack(fill="x", padx=5, pady=2)
        
        lbl = ctk.CTkLabel(row, text=filename, font=ctk.CTkFont(size=11), anchor="w")
        lbl.pack(side="left", padx=10, fill="x", expand=True)
        
        if filename.endswith(".csv"):
            cb = lambda p=full_path: ReportTableModal(self.master, p)
            ctk.CTkButton(row, text="View", width=50, height=22, command=cb).pack(side="left", padx=2)
        else:
            cb = lambda p=full_path: os.startfile(p)
            ctk.CTkButton(row, text="Open", width=50, height=22, fg_color="gray", command=cb).pack(side="left", padx=2)
            
        del_cb = lambda p=full_path: self.delete_report(p)
        ctk.CTkButton(row, text="X", width=25, height=22, fg_color="#e74c3c", command=del_cb).pack(side="right", padx=5)

    def delete_report(self, path):
        if messagebox.askyesno("Confirm", "Delete this report?"):
            os.remove(path)
            if path.endswith(".csv"):
                txt = path.replace(".csv", ".txt")
                if os.path.exists(txt):
                    os.remove(txt)
            self.refresh()

    def clear_all(self):
        if messagebox.askyesno("Confirm", "Delete ALL reports?"):
            d = self.ctx.config.get_reports_dir()
            for f in os.listdir(d):
                os.remove(os.path.join(d, f))
            self.refresh()

    def clear_partial(self, prefix):
        if messagebox.askyesno("Confirm", f"Delete all {prefix} reports?"):
            d = self.ctx.config.get_reports_dir()
            for f in os.listdir(d):
                if prefix in f.lower():
                    os.remove(os.path.join(d, f))
            self.refresh()
