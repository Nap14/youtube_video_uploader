import customtkinter as ctk
from tkinter import filedialog, messagebox

class LessonEditModal(ctk.CTkToplevel):
    def __init__(self, master, schedule, day=None, time=None, value=None, on_save=None, **kwargs):
        super().__init__(master, **kwargs)
        self.schedule = schedule
        self.on_save = on_save
        self.old_day, self.old_time, self.value = day, time, value
        
        self.title("Edit Lesson" if day and time and value else "Add New Lesson")
        self.geometry("700x520")
        self.transient(master)
        self.grab_set()
        self.grid_columnconfigure((0, 1), weight=1)
        self.create_widgets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Day *").grid(row=0, column=0, padx=20, pady=(20,0), sticky="w")
        self.day_cb = ctk.CTkComboBox(self, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], width=250)
        self.day_cb.grid(row=1, column=0, padx=20, pady=5, sticky="w")
        if self.old_day: self.day_cb.set(self.old_day)

        ctk.CTkLabel(self, text="Time *").grid(row=0, column=1, padx=20, pady=(20,0), sticky="w")
        tf = ctk.CTkFrame(self, fg_color="transparent")
        tf.grid(row=1, column=1, padx=20, pady=5, sticky="w")
        self.hour_cb = ctk.CTkComboBox(tf, values=[f"{i:02d}" for i in range(8, 23)], width=100)
        self.hour_cb.pack(side="left")
        ctk.CTkLabel(tf, text=" : ").pack(side="left")
        self.min_cb = ctk.CTkComboBox(tf, values=["00", "15", "30", "45"], width=100)
        self.min_cb.pack(side="left")
        if self.old_time:
            h, m = self.old_time.split(':')
            self.hour_cb.set(h); self.min_cb.set(m if m in ["00", "15", "30", "45"] else "00")

        ctk.CTkLabel(self, text="Course Name *").grid(row=2, column=0, padx=20, pady=(10,0), sticky="w")
        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.grid(row=3, column=0, padx=20, pady=5, sticky="w")
        if self.value: self.name_entry.insert(0, self.value if isinstance(self.value, str) else self.value.get("name", ""))

        ctk.CTkLabel(self, text="LMS Course ID:").grid(row=2, column=1, padx=20, pady=(10,0), sticky="w")
        self.lms_id_entry = ctk.CTkEntry(self, width=300)
        self.lms_id_entry.grid(row=3, column=1, padx=20, pady=5, sticky="w")
        if self.value and isinstance(self.value, dict): self.lms_id_entry.insert(0, self.value.get("lms_course_id", ""))

        self.create_extended_widgets()

    def create_extended_widgets(self):
        ctk.CTkLabel(self, text="Thumbnail:").grid(row=4, column=0, padx=20, pady=(10,0), sticky="w")
        img_f = ctk.CTkFrame(self, fg_color="transparent")
        img_f.grid(row=5, column=0, columnspan=2, padx=20, pady=5, sticky="ew")
        self.img_entry = ctk.CTkEntry(img_f, width=500)
        self.img_entry.pack(side="left", fill="x", expand=True)
        if self.value and isinstance(self.value, dict): self.img_entry.insert(0, self.value.get("thumbnail") or self.value.get("image", ""))
        ctk.CTkButton(img_f, text="Browse", width=80, command=self.browse_img).pack(side="left", padx=(10, 0))

        f_cd = ctk.CTkFrame(self, fg_color="transparent")
        f_cd.grid(row=6, column=0, columnspan=2, padx=20, pady=(10,0), sticky="w")
        
        ctk.CTkLabel(f_cd, text="Duration:").pack(side="left")
        self.dur_entry = ctk.CTkEntry(f_cd, width=70)
        self.dur_entry.pack(side="left", padx=10)
        self.dur_entry.insert(0, "60" if not self.value or isinstance(self.value, str) else str(self.value.get("duration", 60)))
        
        ctk.CTkLabel(f_cd, text="Color:").pack(side="left", padx=(20,0))
        self.color_preview = ctk.CTkLabel(f_cd, text="", width=30, height=20, corner_radius=4, fg_color="gray")
        self.color_preview.pack(side="left", padx=10)
        
        self.chosen_color = self.value.get("color") if isinstance(self.value, dict) else None
        if self.chosen_color: self.color_preview.configure(fg_color=self.chosen_color)
        
        ctk.CTkButton(f_cd, text="Pick", width=60, height=22, command=self.pick_color).pack(side="left")

        bf = ctk.CTkFrame(self, fg_color="transparent")
        bf.grid(row=8, column=0, columnspan=2, padx=20, pady=40, sticky="ew")
        ctk.CTkButton(bf, text="Save", command=self.save, width=120, fg_color="#27ae60").pack(side="left", padx=5)
        if self.old_day and self.old_time and self.value:
            ctk.CTkButton(bf, text="Delete", fg_color="#e74c3c", command=self.delete, width=120).pack(side="left", padx=5)
        ctk.CTkButton(bf, text="Cancel", fg_color="gray", command=self.destroy, width=120).pack(side="right", padx=5)

    def pick_color(self):
        from tkinter import colorchooser
        _, hex_c = colorchooser.askcolor(initialcolor=self.chosen_color or "#3b8ed0")
        if hex_c and self.winfo_exists():
            self.chosen_color = hex_c
            self.color_preview.configure(fg_color=hex_c)

    def browse_img(self):
        f = filedialog.askopenfilename()
        if f: self.img_entry.delete(0, "end"); self.img_entry.insert(0, f)

    def save(self):
        d, t, name = self.day_cb.get(), f"{self.hour_cb.get()}:{self.min_cb.get()}", self.name_entry.get().strip()
        if not d or not name: messagebox.showwarning("Error", "Fill mandatory fields"); return
        
        new_data = (self.value if isinstance(self.value, dict) else {}).copy()
        new_data.update({"name": name, "lms_course_id": self.lms_id_entry.get(), 
                         "duration": int(self.dur_entry.get() if self.dur_entry.get().isdigit() else 60),
                         "thumbnail": self.img_entry.get(), "color": self.chosen_color})
        if "image" in new_data: del new_data["image"]
        
        if d not in self.schedule: self.schedule[d] = {}
        self.schedule[d][t] = new_data
        if self.old_day and self.old_time and (d != self.old_day or t != self.old_time):
            del self.schedule[self.old_day][self.old_time]
        
        if self.on_save: self.on_save()
        self.destroy()

    def delete(self):
        if messagebox.askyesno("Confirm", "Delete lesson?"):
            del self.schedule[self.old_day][self.old_time]
            if self.on_save: self.on_save()
            self.destroy()
