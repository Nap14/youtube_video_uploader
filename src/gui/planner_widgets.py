import os
import customtkinter as ctk

class HistoryLogFrame(ctk.CTkFrame):
    def __init__(self, master, config, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Recent Activity", font=ctk.CTkFont(weight="bold")).pack(pady=10)
        self.history_list = ctk.CTkScrollableFrame(self)
        self.history_list.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh()

    def refresh(self):
        for w in self.history_list.winfo_children(): w.destroy()
        r_dir = self.config.get_reports_dir()
        if not os.path.exists(r_dir): return
        
        files = sorted([f for f in os.listdir(r_dir) if f.startswith("auto_") and f.endswith(".csv")], reverse=True)[:10]
        if not files:
            ctk.CTkLabel(self.history_list, text="No recent auto-jobs", text_color="gray").pack(pady=20)
            return

        for f in files:
            btn_f = ctk.CTkFrame(self.history_list, fg_color=("gray90", "gray20"))
            btn_f.pack(fill="x", pady=2, padx=5)
            ctk.CTkLabel(btn_f, text=f.replace("auto_", ""), font=ctk.CTkFont(size=11)).pack(side="left", padx=10)
            ctk.CTkButton(btn_f, text="View", width=50, height=22, font=ctk.CTkFont(size=10),
                          command=lambda path=os.path.join(r_dir, f): self._view_report(path)).pack(side="right", padx=5)

    def _view_report(self, path):
        from .viewer import ReportTableModal
        ReportTableModal(self, path)
