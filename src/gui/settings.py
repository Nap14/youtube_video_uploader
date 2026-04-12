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
        # Zoom Dir
        ctk.CTkLabel(self, text="Zoom Recordings Directory:").grid(row=1, column=0, padx=30, pady=(10, 0), sticky="w")
        f1 = ctk.CTkFrame(self, fg_color="transparent")
        f1.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="w")
        self.zoom_dir_entry = ctk.CTkEntry(f1, width=ENTRY_WIDTH)
        self.zoom_dir_entry.pack(side="left")
        self.zoom_dir_entry.insert(0, self.config.get_zoom_dir() or "")
        ctk.CTkButton(f1, text="Browse", width=80, command=self.browse_cmd).pack(side="left", padx=(10, 0))
        
        # LMS Token
        ctk.CTkLabel(self, text="LMS Bearer Token:").grid(row=3, column=0, padx=30, pady=(10, 0), sticky="w")
        f2 = ctk.CTkFrame(self, fg_color="transparent")
        f2.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="w")
        self.lms_token_entry = ctk.CTkEntry(f2, width=ENTRY_WIDTH, show="*")
        self.lms_token_entry.pack(side="left")
        self.lms_token_entry.insert(0, self.config.get_lms_token() or "")
        
        self.show_token_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(f2, text="Show", variable=self.show_token_var, command=self.toggle_token, width=60).pack(side="left", padx=(10, 0))

        # ID & Save
        ctk.CTkLabel(self, text="School ID:").grid(row=5, column=0, padx=30, pady=(10, 0), sticky="w")
        self.school_id_entry = ctk.CTkEntry(self, width=200)
        self.school_id_entry.grid(row=6, column=0, padx=30, pady=(0, 20), sticky="w")
        self.school_id_entry.insert(0, self.config.get_school_id() or "18828")

        ctk.CTkButton(self, text="Save Settings", command=self.save_cmd, width=150).grid(row=7, column=0, padx=30, pady=20, sticky="w")

    def toggle_token(self):
        self.lms_token_entry.configure(show="" if self.show_token_var.get() else "*")
