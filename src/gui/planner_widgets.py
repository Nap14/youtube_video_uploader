import os
import customtkinter as ctk
from src.core.context import AppContext
from src.gui.base_frame import BaseFrame
from .viewer import ReportTableModal

class HistoryLogFrame(BaseFrame):
    def __init__(self, master, ctx: AppContext, **kwargs):
        super().__init__(master, ctx, **kwargs)

    def _create_widgets(self):
        ctk.CTkLabel(self, text="Recent Activity", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.history_list = ctk.CTkScrollableFrame(self)
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

    def refresh(self):
        for w in self.history_list.winfo_children():
            w.destroy()
            
        r_dir = self.ctx.config.get_reports_dir()
        if not os.path.exists(r_dir):
            return
        
        files = self._get_recent_files(r_dir)
        if not files:
            ctk.CTkLabel(self.history_list, text="No recent auto-jobs", text_color="gray").pack(pady=20)
            return

        for f in files:
            self._add_history_item(f, r_dir)

    def _get_recent_files(self, r_dir):
        files = [f for f in os.listdir(r_dir) if f.startswith("auto_") and f.endswith(".csv")]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(r_dir, x)), reverse=True)
        return files[:10]

    def _add_history_item(self, filename, r_dir):
        btn_f = ctk.CTkFrame(self.history_list, fg_color=("gray90", "gray20"))
        btn_f.pack(fill="x", pady=2, padx=5)
        
        display_name = filename.replace("auto_", "")
        ctk.CTkLabel(btn_f, text=display_name, font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
        
        path = os.path.join(r_dir, filename)
        ctk.CTkButton(
            btn_f, text="View", width=50, height=22, font=ctk.CTkFont(size=10),
            command=lambda p=path: self._view_report(p)
        ).pack(side="right", padx=5)

    def _view_report(self, path):
        ReportTableModal(self.master, path)
