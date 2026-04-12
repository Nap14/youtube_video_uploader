import customtkinter as ctk
from .planner_widgets import HistoryLogFrame

class PlannerFrame(ctk.CTkFrame):
    def __init__(self, master, config, **kwargs):
        super().__init__(master, **kwargs)
        self.config = config
        self.p_cfg = self.config.get_planner_config()
        self.create_widgets()

    def create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        header_f = ctk.CTkFrame(self, fg_color="transparent")
        header_f.grid(row=0, column=0, columnspan=2, padx=30, pady=(30, 20), sticky="ew")
        
        ctk.CTkLabel(header_f, text="Automation Planner", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.enabled_var = ctk.BooleanVar(value=self.p_cfg.get("enabled", False))
        self.main_switch = ctk.CTkSwitch(header_f, text="", variable=self.enabled_var, 
                                          command=self.toggle_inputs, width=50,
                                          progress_color="#2ecc71")
        self.main_switch.pack(side="left", padx=30)
        
        self.settings_f = ctk.CTkFrame(self, fg_color="transparent")
        self.settings_f.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.settings_f.grid_columnconfigure(0, weight=1)

        self.inputs_f = ctk.CTkFrame(self.settings_f, fg_color="transparent")
        self.inputs_f.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.inputs_f, text="Frequency:").grid(row=0, column=0, padx=10, pady=(10, 0), sticky="w")
        self.freq_cb = ctk.CTkComboBox(self.inputs_f, values=["hourly", "daily", "weekly"], command=self.update_ui_no_save)
        self.freq_cb.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.freq_cb.set(self.p_cfg.get("frequency", "daily"))

        self.dynamic_f = ctk.CTkFrame(self.inputs_f, fg_color="transparent")
        self.dynamic_f.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        ctk.CTkLabel(self.inputs_f, text="Automation Mode:").grid(row=3, column=0, padx=10, pady=(20, 0), sticky="w")
        self.mode_var = ctk.StringVar(value=self.p_cfg.get("mode", "1"))
        self.r1 = ctk.CTkRadioButton(self.inputs_f, text="YouTube + LMS", variable=self.mode_var, value="1")
        self.r1.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.r2 = ctk.CTkRadioButton(self.inputs_f, text="YouTube Only", variable=self.mode_var, value="2")
        self.r2.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.confirm_var = ctk.BooleanVar(value=self.p_cfg.get("require_confirmation", True))
        self.confirm_var_ck = ctk.CTkCheckBox(self.inputs_f, text="Require confirmation before start", variable=self.confirm_var)
        self.confirm_var_ck.grid(row=6, column=0, padx=10, pady=20, sticky="w")

        self.actions_f = ctk.CTkFrame(self.settings_f, fg_color="transparent")
        self.settings_f.grid_rowconfigure(9, weight=1)
        self.actions_f.grid(row=10, column=0, padx=10, pady=20, sticky="sw")
        ctk.CTkButton(self.actions_f, text="Save Settings", command=self.save, width=150, fg_color="#3498db").pack(side="left")
        self.status_label = ctk.CTkLabel(self.actions_f, text="", text_color="#2ecc71", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=20)

        self.log_f = HistoryLogFrame(self, self.config)
        self.log_f.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")
        
        self.update_ui_no_save()

    def refresh_history(self):
        self.log_f.refresh()

    def update_ui_no_save(self, _=None):
        for w in self.dynamic_f.winfo_children(): w.destroy()
        freq = self.freq_cb.get()
        if freq == "hourly":
            ctk.CTkLabel(self.dynamic_f, text="Every (hours):").pack(side="left")
            self.int_entry = ctk.CTkEntry(self.dynamic_f, width=60)
            self.int_entry.pack(side="left", padx=10)
            self.int_entry.insert(0, str(self.p_cfg.get("interval", 1)))
        elif freq == "daily" or freq == "weekly":
            if freq == "weekly":
                self.day_cb = ctk.CTkComboBox(self.dynamic_f, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
                self.day_cb.pack(side="left")
                self.day_cb.set(self.p_cfg.get("day", "Monday"))
            ctk.CTkLabel(self.dynamic_f, text="Time (HH:MM):").pack(side="left", padx=10)
            self.time_entry = ctk.CTkEntry(self.dynamic_f, width=80 if freq == "weekly" else 100)
            self.time_entry.pack(side="left")
            self.time_entry.insert(0, self.p_cfg.get("time", "20:00"))
        self.toggle_inputs()

    def toggle_inputs(self):
        if self.enabled_var.get():
            self.inputs_f.grid(row=0, column=0, sticky="nsew")
        else:
            self.inputs_f.grid_forget()

    def save(self):
        cfg = {"enabled": self.enabled_var.get(), "frequency": self.freq_cb.get(), 
               "mode": self.mode_var.get(), "require_confirmation": self.confirm_var.get()}
        if cfg["frequency"] == "hourly" and hasattr(self, 'int_entry'):
            cfg["interval"] = int(self.int_entry.get() if self.int_entry.get().isdigit() else 1)
        elif hasattr(self, 'time_entry'):
            cfg["time"] = self.time_entry.get()
            if cfg["frequency"] == "weekly": cfg["day"] = self.day_cb.get()
        self.config.save_planner_config(cfg)
        self.toggle_inputs()
        self.status_label.configure(text="Settings Saved!")
        self.after(3000, lambda: self.status_label.configure(text=""))
