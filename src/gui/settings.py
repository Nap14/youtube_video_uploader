import customtkinter as ctk

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, config, paths, browse_cmd, save_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.paths = paths
        self.browse_cmd = browse_cmd
        self.save_cmd = save_cmd
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="General Settings", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=30, pady=(30, 20), sticky="w")
        
        ENTRY_WIDTH = 550
        self._add_label_with_help("Zoom Recordings Directory:", "The local folder where Zoom saves your recordings. Usually: Documents/Zoom")
        f1 = ctk.CTkFrame(self, fg_color="transparent")
        f1.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="w")
        self.zoom_dir_entry = ctk.CTkEntry(f1, width=ENTRY_WIDTH)
        self.zoom_dir_entry.pack(side="left")
        self.zoom_dir_entry.insert(0, self.config.get_zoom_dir() or "")
        ctk.CTkButton(f1, text="Browse", width=80, command=self.browse_cmd).pack(side="left", padx=(10, 0))
        
        self._add_label_with_help("LMS Bearer Token:", "Bearer token from SendPulse Settings -> API -> Educate, OR from browser Network tab while editing a lesson.")
        f2 = ctk.CTkFrame(self, fg_color="transparent")
        f2.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="w")
        self.lms_token_entry = ctk.CTkEntry(f2, width=ENTRY_WIDTH, show="*")
        self.lms_token_entry.pack(side="left")
        self.lms_token_entry.insert(0, self.config.get_lms_token() or "")
        
        self.show_token_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(f2, text="Show", variable=self.show_token_var, command=self.toggle_token, width=60).pack(side="left", padx=(10, 0))

        self._add_label_with_help("School ID:", "Your SendPulse School Identification Number.")
        self.school_id_entry = ctk.CTkEntry(self, width=200)
        self.school_id_entry.grid(row=6, column=0, padx=30, pady=(0, 20), sticky="w")
        self.school_id_entry.insert(0, self.config.get_school_id() or "")

        ctk.CTkButton(self, text="Save Settings", command=self.save_cmd, width=150).grid(row=7, column=0, padx=30, pady=20, sticky="w")

    def _add_label_with_help(self, text, help_msg):
        row = (self.grid_size()[1])
        f = ctk.CTkFrame(self, fg_color="transparent")
        f.grid(row=row, column=0, padx=30, pady=(10, 0), sticky="w")
        ctk.CTkLabel(f, text=text).pack(side="left")
        ctk.CTkButton(f, text="?", width=20, height=20, corner_radius=10, fg_color="gray", 
                      command=lambda: self.show_help(text, help_msg)).pack(side="left", padx=5)

    def show_help(self, title, msg):
        from tkinter import messagebox
        messagebox.showinfo(title, msg)

    def toggle_token(self):
        self.lms_token_entry.configure(show="" if self.show_token_var.get() else "*")
