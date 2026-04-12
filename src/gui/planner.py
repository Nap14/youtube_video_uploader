import customtkinter as ctk

class PlannerFrame(ctk.CTkFrame):
    def __init__(self, master, config, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.p_cfg = self.config.get_planner_config()
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(self, text="Automation Planner", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, padx=30, pady=(30, 10), sticky="w")
        
        # Master Toggle
        self.enabled_var = ctk.BooleanVar(value=self.p_cfg.get("enabled", False))
        ctk.CTkSwitch(self, text="Enable Automation Service", variable=self.enabled_var, 
                       font=ctk.CTkFont(size=14, weight="bold")).grid(row=1, column=0, padx=30, pady=20, sticky="w")

        # Frequency
        ctk.CTkLabel(self, text="Frequency:").grid(row=2, column=0, padx=30, pady=(10, 0), sticky="w")
        self.freq_cb = ctk.CTkComboBox(self, values=["hourly", "daily", "weekly"], command=self.update_ui_no_save)
        self.freq_cb.grid(row=3, column=0, padx=30, pady=5, sticky="w")
        self.freq_cb.set(self.p_cfg.get("frequency", "daily"))

        # Dynamic Field Container
        self.dynamic_f = ctk.CTkFrame(self, fg_color="transparent")
        self.dynamic_f.grid(row=4, column=0, padx=30, pady=10, sticky="w")
        
        # Mode
        ctk.CTkLabel(self, text="Automation Mode:").grid(row=5, column=0, padx=30, pady=(20, 0), sticky="w")
        self.mode_var = ctk.StringVar(value=self.p_cfg.get("mode", "1"))
        self.r1 = ctk.CTkRadioButton(self, text="YouTube + LMS", variable=self.mode_var, value="1")
        self.r1.grid(row=6, column=0, padx=30, pady=5, sticky="w")
        self.r2 = ctk.CTkRadioButton(self, text="YouTube Only", variable=self.mode_var, value="2")
        self.r2.grid(row=7, column=0, padx=30, pady=5, sticky="w")

        self.confirm_var = ctk.BooleanVar(value=self.p_cfg.get("require_confirmation", True))
        self.confirm_var_ck = ctk.CTkCheckBox(self, text="Require confirmation before start", variable=self.confirm_var)
        self.confirm_var_ck.grid(row=8, column=0, padx=30, pady=20, sticky="w")

        ctk.CTkButton(self, text="Save", command=self.save, width=200).grid(row=9, column=0, padx=30, pady=20, sticky="w")
        self.update_ui_no_save()

    def update_ui_no_save(self, _=None):
        for w in self.dynamic_f.winfo_children(): w.destroy()
        freq = self.freq_cb.get()
        if freq == "hourly":
            ctk.CTkLabel(self.dynamic_f, text="Every (hours):").pack(side="left")
            self.int_entry = ctk.CTkEntry(self.dynamic_f, width=60)
            self.int_entry.pack(side="left", padx=10)
            self.int_entry.insert(0, str(self.p_cfg.get("interval", 1)))
        elif freq == "daily":
            ctk.CTkLabel(self.dynamic_f, text="At Time (HH:MM):").pack(side="left")
            self.time_entry = ctk.CTkEntry(self.dynamic_f, width=100)
            self.time_entry.pack(side="left", padx=10)
            self.time_entry.insert(0, self.p_cfg.get("time", "20:00"))
        elif freq == "weekly":
            self.day_cb = ctk.CTkComboBox(self.dynamic_f, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
            self.day_cb.pack(side="left")
            self.day_cb.set(self.p_cfg.get("day", "Monday"))
            self.time_entry = ctk.CTkEntry(self.dynamic_f, width=80)
            self.time_entry.pack(side="left", padx=10)
            self.time_entry.insert(0, self.p_cfg.get("time", "20:00"))
        self.toggle_inputs()

    def toggle_inputs(self):
        state = "normal" if self.enabled_var.get() else "disabled"
        for w in [self.freq_cb, self.confirm_var_ck, self.r1, self.r2]:
            if hasattr(w, "configure"): w.configure(state=state)
        # Also handle dynamic frame children
        for w in self.dynamic_f.winfo_children():
            if hasattr(w, "configure"): w.configure(state=state)

    def save(self):
        cfg = {
            "enabled": self.enabled_var.get(),
            "frequency": self.freq_cb.get(),
            "mode": self.mode_var.get(),
            "require_confirmation": self.confirm_var.get()
        }
        if cfg["frequency"] == "hourly" and hasattr(self, 'int_entry'):
            cfg["interval"] = int(self.int_entry.get() if self.int_entry.get().isdigit() else 1)
        elif hasattr(self, 'time_entry'):
            cfg["time"] = self.time_entry.get()
            if cfg["frequency"] == "weekly": cfg["day"] = self.day_cb.get()
        self.config.save_planner_config(cfg)
        self.toggle_inputs()
