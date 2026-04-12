import customtkinter as ctk
from .constants import COURSE_COLORS, DAYS_EN, DAYS_UA
import hashlib

class ScheduleCalendarFrame(ctk.CTkScrollableFrame):
    def __init__(self, master, schedule, edit_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self.schedule = schedule
        self.edit_cmd = edit_cmd
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(list(range(1, 8)), weight=1)

    def get_course_color(self, name):
        normalized = name.strip().lower()
        h = int(hashlib.md5(normalized.encode()).hexdigest(), 16)
        return COURSE_COLORS[h % len(COURSE_COLORS)]

    def refresh(self):
        for child in self.winfo_children(): child.destroy()
        for i, name in enumerate(DAYS_UA):
            ctk.CTkLabel(self, text=name, font=ctk.CTkFont(weight="bold")).grid(row=0, column=i+1, pady=10, sticky="ew")

        # Hourly Grid
        for row in range(1, 16):
            hour = 7 + row
            ctk.CTkLabel(self, text=f"{hour}:00", font=ctk.CTkFont(size=10), text_color="gray60").grid(row=row, column=0, padx=(0, 10), sticky="ne")
            for col in range(1, 8):
                ctk.CTkButton(self, text="", fg_color="transparent", border_width=1, border_color=("gray95", "gray25"), 
                              hover_color=("gray85", "gray35"), corner_radius=0, height=50,
                              command=lambda d=DAYS_EN[col-1], t=f"{hour}:00": self.edit_cmd(d, t)).grid(row=row, column=col, sticky="nsew")

        self.populate_lessons()

    def populate_lessons(self):
        for day_idx, day_name in enumerate(DAYS_EN):
            day_data = self.schedule.get(day_name, {})
            for time_str, data in day_data.items():
                try:
                    h, _ = map(int, time_str.split(':'))
                    row_idx = h - 7
                    if row_idx < 1: continue
                    name = data if isinstance(data, str) else data.get("name", "Unnamed")
                    duration = 60 if isinstance(data, str) else int(data.get("duration", 60))
                    
                    # Color logic: manual or hashed
                    manual_c = None if isinstance(data, str) else data.get("color")
                    row_span, (cl, cd) = max(1, duration // 60), (manual_c, manual_c) if manual_c else self.get_course_color(name)
                    
                    wrapped = "\n".join([name[i:i+12] for i in range(0, len(name), 12)]) if len(name) > 12 else name
                    btn = ctk.CTkButton(self, text=wrapped, fg_color=(cl, cd), text_color=("black", "white"), 
                                        font=ctk.CTkFont(size=10, weight="bold"), height=48 * row_span,
                                        command=lambda d=day_name, t=time_str, v=data: self.edit_cmd(d, t, v))
                    btn.grid(row=row_idx, column=day_idx+1, rowspan=row_span, padx=2, pady=2, sticky="nsew")
                except: continue
