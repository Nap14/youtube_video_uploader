import customtkinter as ctk
from tkinter import filedialog, messagebox, colorchooser

from src.services.ui_service import UIService

class LessonEditModal(ctk.CTkToplevel):
    def __init__(self, master, schedule, day=None, time=None, value=None, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.schedule = schedule
        self.on_save = on_save
        self.old_day = day
        self.old_time = time
        self.value = value
        
        self._setup_window(master)
        self._create_widgets()

    def _setup_window(self, master):
        title = "Edit Lesson" if self.old_day else "Add Lesson"
        self.title(title)
        self.geometry("700x520")
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure((0, 1), weight=1)

    def _create_widgets(self):
        self._init_day_time_section()
        self._init_course_info_section()
        self._init_thumbnail_section()
        self._init_extra_settings_section()
        self._init_action_buttons()

    def _init_day_time_section(self):
        ctk.CTkLabel(self, text="Day *").grid(row=0, column=0, padx=20, pady=(15, 0), sticky="w")
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        self.day_cb = ctk.CTkComboBox(self, values=days, width=250)
        self.day_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        if self.old_day:
            self.day_cb.set(self.old_day)

        ctk.CTkLabel(self, text="Time *").grid(row=0, column=1, padx=20, pady=(15, 0), sticky="w")
        tf = ctk.CTkFrame(self, fg_color="transparent")
        tf.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        
        hours = [f"{i:02d}" for i in range(8, 23)]
        self.h_cb = ctk.CTkComboBox(tf, values=hours, width=100)
        self.h_cb.pack(side="left")
        
        ctk.CTkLabel(tf, text=" : ").pack(side="left")
        
        mins = ["00", "15", "30", "45"]
        self.m_cb = ctk.CTkComboBox(tf, values=mins, width=100)
        self.m_cb.pack(side="left")
        
        if self.old_time:
            h, m = self.old_time.split(':')
            self.h_cb.set(h)
            m_val = m if m in mins else "00"
            self.m_cb.set(m_val)

    def _init_course_info_section(self):
        ctk.CTkLabel(self, text="Course Name *").grid(row=2, column=0, padx=20, pady=(10, 0), sticky="w")
        self.n_ent = ctk.CTkEntry(self, width=300)
        self.n_ent.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        
        if self.value:
            val = self.value if isinstance(self.value, str) else self.value.get("name", "")
            self.n_ent.insert(0, val)

        ctk.CTkLabel(self, text="LMS Course ID:").grid(row=2, column=1, padx=20, pady=(10, 0), sticky="w")
        self.l_id_ent = ctk.CTkEntry(self, width=300)
        self.l_id_ent.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        
        if isinstance(self.value, dict):
            self.l_id_ent.insert(0, self.value.get("lms_course_id", ""))

    def _init_thumbnail_section(self):
        ctk.CTkLabel(self, text="Thumbnail:").grid(row=4, column=0, padx=20, pady=(10, 0), sticky="w")
        img_f = ctk.CTkFrame(self, fg_color="transparent")
        img_f.grid(row=5, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        
        self.img_ent = ctk.CTkEntry(img_f, width=500)
        self.img_ent.pack(side="left", fill="x", expand=True)
        
        if isinstance(self.value, dict):
            self.img_ent.insert(0, self.value.get("thumbnail") or "")
            
        ctk.CTkButton(img_f, text="Browse", width=80, command=self._browse).pack(side="left", padx=10)

    def _init_extra_settings_section(self):
        f_cd = ctk.CTkFrame(self, fg_color="transparent")
        f_cd.grid(row=6, column=0, columnspan=2, padx=20, pady=10, sticky="w")
        
        ctk.CTkLabel(f_cd, text="Duration:").pack(side="left")
        self.dur_ent = ctk.CTkEntry(f_cd, width=70)
        self.dur_ent.pack(side="left", padx=10)
        
        dur_val = "60"
        if isinstance(self.value, dict):
            dur_val = str(self.value.get("duration", 60))
        self.dur_ent.insert(0, dur_val)
        
        ctk.CTkLabel(f_cd, text="Color:").pack(side="left", padx=(20, 0))
        self.c_pre = ctk.CTkLabel(f_cd, text="", width=30, height=20, corner_radius=4, fg_color="gray")
        self.c_pre.pack(side="left", padx=10)
        
        self.color = self.value.get("color") if isinstance(self.value, dict) else None
        if self.color:
            self.c_pre.configure(fg_color=self.color)
            
        ctk.CTkButton(f_cd, text="Pick", width=60, height=22, command=self._pick_color).pack(side="left")

    def _init_action_buttons(self):
        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.grid(row=8, column=0, columnspan=2, padx=20, pady=30, sticky="ew")
        
        ctk.CTkButton(bf, text="Save", command=self._save, width=120, fg_color="#27ae60").pack(side="left", padx=5)
        
        if self.old_day and self.value:
            ctk.CTkButton(bf, text="Delete", fg_color="#e74c3c", command=self._delete, width=120).pack(side="left", padx=5)
            
        ctk.CTkButton(bf, text="Cancel", fg_color="gray", command=self.destroy, width=120).pack(side="right", padx=5)

    def _pick_color(self):
        _, hex_c = colorchooser.askcolor(initialcolor=self.color or "#3b8ed0")
        if hex_c:
            self.color = hex_c
            self.c_pre.configure(fg_color=hex_c)

    def _browse(self):
        f = filedialog.askopenfilename()
        if f:
            self.img_ent.delete(0, "end")
            self.img_ent.insert(0, f)

    def _save(self):
        d = self.day_cb.get()
        t = f"{self.h_cb.get()}:{self.m_cb.get()}"
        n = self.n_ent.get().strip()
        
        if not d or not n:
            UIService.error("Error", "Fill required fields")
            return
            
        self._perform_save(d, t, n)

    def _perform_save(self, d, t, n):
        data = (self.value if isinstance(self.value, dict) else {}).copy()
        data.update({
            "name": n, 
            "lms_course_id": self.l_id_ent.get(), 
            "duration": int(self.dur_ent.get() if self.dur_ent.get().isdigit() else 60), 
            "thumbnail": self.img_ent.get(), 
            "color": self.color
        })
        
        if d not in self.schedule:
            self.schedule[d] = {}
        self.schedule[d][t] = data
        
        if self.old_day and self.old_time and (d != self.old_day or t != self.old_time):
            del self.schedule[self.old_day][self.old_time]
            
        if self.on_save:
            self.on_save()
        self.destroy()

    def _delete(self):
        if messagebox.askyesno("Confirm", "Delete lesson?"):
            del self.schedule[self.old_day][self.old_time]
            if self.on_save:
                self.on_save()
            self.destroy()
