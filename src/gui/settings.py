import customtkinter as ctk

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, config, paths, browse_cmd, save_cmd, theme_cmd, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.paths = paths
        self.browse_cmd = browse_cmd
        self.save_cmd = save_cmd
        self.theme_cmd = theme_cmd
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="General Settings", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=30, pady=(20, 10), sticky="w")
        
        ENTRY_WIDTH = 550
        # Theme
        self._add_label_with_help("Appearance Mode:", "Change the visual theme of the application.")
        self.theme_menu = ctk.CTkOptionMenu(self, values=["Light", "Dark", "System"], command=self.theme_cmd)
        self.theme_menu.grid(row=2, column=0, padx=30, pady=(0, 20), sticky="w")
        self.theme_menu.set(self.config.get_data().get("THEME", "Dark"))

        # Zoom Dir
        self._add_label_with_help("Zoom Recordings Directory:", "The local folder where Zoom saves your recordings. Usually: Documents/Zoom")
        f1 = ctk.CTkFrame(self, fg_color="transparent")
        f1.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="w")
        self.zoom_dir_entry = ctk.CTkEntry(f1, width=ENTRY_WIDTH)
        self.zoom_dir_entry.pack(side="left")
        self.zoom_dir_entry.insert(0, self.config.get_zoom_dir() or "")
        ctk.CTkButton(f1, text="Browse", width=80, command=self.browse_cmd).pack(side="left", padx=(10, 0))
        
        # LMS Token
        self._add_label_with_help("LMS Bearer Token:", "Bearer token from SendPulse Settings -> API -> Educate, OR from browser Network tab while editing a lesson.")
        f2 = ctk.CTkFrame(self, fg_color="transparent")
        f2.grid(row=6, column=0, padx=30, pady=(0, 10), sticky="w")
        self.lms_token_entry = ctk.CTkEntry(f2, width=ENTRY_WIDTH, show="*")
        self.lms_token_entry.pack(side="left")
        self.lms_token_entry.insert(0, self.config.get_lms_token() or "")
        
        self.show_token_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(f2, text="Show", variable=self.show_token_var, command=self.toggle_token, width=60).pack(side="left", padx=(10, 0))

        # ID & Save
        self._add_label_with_help("School ID:", "Your SendPulse School Identification Number.")
        self.school_id_entry = ctk.CTkEntry(self, width=200)
        self.school_id_entry.grid(row=8, column=0, padx=30, pady=(0, 20), sticky="w")
        self.school_id_entry.insert(0, self.config.get_school_id() or "")

        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.grid(row=9, column=0, padx=30, pady=20, sticky="w")
        ctk.CTkButton(sf, text="Save Settings", command=self.save_cmd, width=150).pack(side="left")
        self.status_label = ctk.CTkLabel(sf, text="", text_color="#2ecc71", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=20)

    def show_status(self, text="Settings Saved!"):
        self.status_label.configure(text=text)
        self.after(3000, lambda: self.status_label.configure(text=""))

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
