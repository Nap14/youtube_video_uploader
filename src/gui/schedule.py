import customtkinter as ctk
from src.core.context import AppContext
from src.gui.base_frame import BaseFrame
from src.services.schedule_utils import save_schedule
from .modals.lesson import LessonEditModal

class ScheduleCalendarFrame(BaseFrame):
    def __init__(self, master, ctx: AppContext, **kwargs):
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.hours = [f"{h:02d}:00" for h in range(8, 24)]
        super().__init__(master, ctx, **kwargs)

    def _create_widgets(self):
        self._init_header()
        
        # Sticky Days Header (Not scrollable)
        self.header_f = ctk.CTkFrame(self, fg_color="transparent")
        self.header_f.grid(row=1, column=0, padx=20, pady=(0, 0), sticky="ew")
        self._render_days_header()
        
        # Scrollable Area for Grid
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.refresh()

    def _init_header(self):
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=0, column=0, padx=30, pady=(30, 5), sticky="ew")
        ctk.CTkLabel(h, text="Weekly Schedule", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        ctk.CTkButton(h, text="+ Add Lesson", width=120, command=self._add_lesson).pack(side="right", padx=10)

    def _render_days_header(self):
        # Placeholder for Time column visibility
        self.header_f.grid_columnconfigure(0, minsize=60)
        for i, d in enumerate(self.days):
            self.header_f.grid_columnconfigure(i + 1, weight=1, minsize=140)
            ctk.CTkLabel(self.header_f, text=d, font=ctk.CTkFont(weight="bold"), 
                         fg_color=("gray85", "gray25"), height=35, corner_radius=6).grid(row=0, column=i+1, sticky="ew", padx=2)

    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()
            
        self.scroll.grid_columnconfigure(0, minsize=60)
        for i in range(len(self.days)):
            self.scroll.grid_columnconfigure(i + 1, weight=1, minsize=140)

        # Track occupied slots for rowspan [day][hour_idx]
        occupied = {day: set() for day in self.days}
        
        for r_idx, time in enumerate(self.hours):
            # Time label
            ctk.CTkLabel(self.scroll, text=time, font=ctk.CTkFont(size=11, weight="bold")).grid(row=r_idx, column=0, pady=15)
            
            for c_idx, day in enumerate(self.days):
                if r_idx in occupied[day]:
                    continue
                
                lesson = self.ctx.schedule.get(day, {}).get(time)
                if lesson:
                    # Calculate duration
                    duration = lesson.get("duration", 60) if isinstance(lesson, dict) else 60
                    row_span = max(1, round(duration / 60))
                    
                    # Mark slots as occupied
                    for i in range(row_span):
                        occupied[day].add(r_idx + i)
                    
                    self._render_lesson_card(day, time, lesson, c_idx + 1, r_idx, row_span)
                else:
                    self._render_empty_cell(day, time, c_idx + 1, r_idx)

    def _render_lesson_card(self, day, time, val, col, row, rowspan):
        name = val if isinstance(val, str) else val.get("name", "Unknown")
        color = val.get("color") if isinstance(val, dict) else None
        
        # New Text Format: Split by /, take 2 parts, newline
        parts = [p.strip() for p in name.split('/')]
        display_text = "\n".join(parts[:2])
        
        # Using Button for better interaction and built-in hover
        btn = ctk.CTkButton(
            self.scroll, text=display_text, 
            fg_color=color or ("gray80", "gray30"),
            hover_color=self._adjust_color(color or ("gray80", "gray30")),
            text_color=("black", "white"),
            font=ctk.CTkFont(size=11, weight="bold"),
            corner_radius=6, border_width=0,
            command=lambda d=day, t=time, v=val: self._edit_lesson(d, t, v)
        )
        btn.grid(row=row, column=col, rowspan=rowspan, sticky="nsew", padx=3, pady=2)

    def _render_empty_cell(self, day, time, col, row):
        btn = ctk.CTkButton(
            self.scroll, text="", fg_color="transparent", border_width=1, 
            border_color=("gray85", "gray25"), hover_color=("gray75", "gray30"),
            height=50, corner_radius=4,
            command=lambda d=day, t=time: self._add_lesson_at(d, t)
        )
        btn.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

    def _adjust_color(self, base_color):
        # Simple highlight logic: if it's a tuple (light, dark) or string
        if isinstance(base_color, tuple):
            return ("gray70", "gray40")
        return None # Let CTk handle default hover if we don't have a specific color

    def _add_lesson_at(self, day, time):
        LessonEditModal(self, self.ctx.schedule, day=day, time=time, on_save=self._on_save)

    def _add_lesson(self):
        LessonEditModal(self, self.ctx.schedule, on_save=self._on_save)

    def _edit_lesson(self, day, time, value):
        LessonEditModal(self, self.ctx.schedule, day, time, value, on_save=self._on_save)

    def _on_save(self):
        save_schedule(self.ctx.paths.schedule_file, self.ctx.schedule)
        self.refresh()
