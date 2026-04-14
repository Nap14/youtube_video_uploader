import customtkinter as ctk
from typing import Any

from src.core.context import AppContext
from src.gui.base_frame import BaseFrame
from .planner_widgets import HistoryLogFrame

class PlannerFrame(BaseFrame):
    def __init__(self, master: Any, ctx: AppContext, **kwargs: Any):
        super().__init__(master, ctx, **kwargs)

    def _create_widgets(self):
        self.p_cfg = self.ctx.config.get_planner_config()
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._init_header()
        
        # Left container for inputs + persistent save button
        left_f = ctk.CTkFrame(self, fg_color="transparent")
        left_f.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        left_f.grid_rowconfigure(0, weight=1) # inputs space
        left_f.grid_columnconfigure(0, weight=1)

        self.inp_f = ctk.CTkFrame(left_f, fg_color="transparent")
        self.inp_f.grid(row=0, column=0, sticky="nsew")
        self.inp_f.grid_columnconfigure(0, weight=1)

        self._init_inputs_container()
        self._init_save_button(left_f) # Attached to the bottom of the left frame
        
        self._init_history_log()
        self._update_ui()

    def _init_header(self):
        h_f = ctk.CTkFrame(self, fg_color="transparent")
        h_f.grid(row=0, column=0, columnspan=2, padx=30, pady=(30, 20), sticky="ew")
        
        ctk.CTkLabel(h_f, text="Automation Planner", font=ctk.CTkFont(size=24, weight="bold")).pack(side="left")
        
        self.en_var = ctk.BooleanVar(value=self.p_cfg.get("enabled", False))
        ctk.CTkSwitch(
            h_f, text="", variable=self.en_var, command=self._toggle, 
            width=50, progress_color="#2ecc71"
        ).pack(side="left", padx=30)

    def _init_inputs_container(self):
        self._init_frequency_selector()
        
        self.dyn_f = ctk.CTkFrame(self.inp_f, fg_color="transparent")
        self.dyn_f.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self._init_mode_selector()

    def _init_frequency_selector(self):
        ctk.CTkLabel(self.inp_f, text="Frequency:").grid(row=0, column=0, padx=10, sticky="w")
        self.freq_cb = ctk.CTkComboBox(
            self.inp_f, values=["hourly", "daily", "weekly"], command=self._update_ui
        )
        self.freq_cb.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.freq_cb.set(self.p_cfg.get("frequency", "daily"))

    def _init_mode_selector(self):
        ctk.CTkLabel(self.inp_f, text="Mode:").grid(row=3, column=0, padx=10, pady=(10, 0), sticky="w")
        self.mode_var = ctk.StringVar(value=self.p_cfg.get("mode", "1"))
        
        r1 = ctk.CTkRadioButton(self.inp_f, text="YT + LMS", variable=self.mode_var, value="1")
        r1.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        r2 = ctk.CTkRadioButton(self.inp_f, text="YT Only", variable=self.mode_var, value="2")
        r2.grid(row=5, column=0, padx=10, pady=5, sticky="w")

        self.conf_var = ctk.BooleanVar(value=self.p_cfg.get("require_confirmation", True))
        ctk.CTkCheckBox(self.inp_f, text="Require confirmation", variable=self.conf_var).grid(row=6, column=0, padx=10, pady=20, sticky="w")

    def _init_save_button(self, parent):
        btn_f = ctk.CTkFrame(parent, fg_color="transparent")
        btn_f.grid(row=1, column=0, padx=10, pady=20, sticky="sw")
        ctk.CTkButton(btn_f, text="Save Settings", command=self._save, width=150, height=35).pack(side="left")
        self.st_lbl = ctk.CTkLabel(btn_f, text="", text_color="#2ecc71")
        self.st_lbl.pack(side="left", padx=20)

    def _init_history_log(self):
        self.log_f = HistoryLogFrame(self, self.ctx)
        self.log_f.grid(row=1, column=1, padx=20, pady=10, sticky="nsew")

    def refresh(self): 
        self.log_f.refresh()

    def _update_ui(self, _=None):
        for w in self.dyn_f.winfo_children():
            w.destroy()
            
        freq = self.freq_cb.get()
        if freq == "hourly":
            self._setup_hourly_ui()
        else:
            self._setup_timed_ui(freq)
            
        self._toggle()

    def _setup_hourly_ui(self):
        ctk.CTkLabel(self.dyn_f, text="Every (h):").pack(side="left")
        self.int_ent = ctk.CTkEntry(self.dyn_f, width=60)
        self.int_ent.pack(side="left", padx=10)
        self.int_ent.insert(0, str(self.p_cfg.get("interval", 1)))

    def _setup_timed_ui(self, freq: str):
        if freq == "weekly":
            self.day_cb = ctk.CTkComboBox(
                self.dyn_f, 
                values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            )
            self.day_cb.pack(side="left")
            self.day_cb.set(self.p_cfg.get("day", "Monday"))
            
        ctk.CTkLabel(self.dyn_f, text="Time:").pack(side="left", padx=10)
        self.tm_ent = ctk.CTkEntry(self.dyn_f, width=80)
        self.tm_ent.pack(side="left")
        self.tm_ent.insert(0, self.p_cfg.get("time", "20:00"))

    def _toggle(self):
        if self.en_var.get():
            self.inp_f.grid()
        else:
            self.inp_f.grid_remove() # Using grid_remove to preserve row/col structure but hide content

    def _save(self):
        cfg = {
            "enabled": self.en_var.get(), 
            "frequency": self.freq_cb.get(), 
            "mode": self.mode_var.get(), 
            "require_confirmation": self.conf_var.get()
        }
        
        self._collect_dynamic_settings(cfg)
        self.ctx.config.save_planner_config(cfg)
        self.p_cfg = cfg
        
        self.st_lbl.configure(text="Saved!")
        self.after(3000, lambda: self.st_lbl.configure(text=""))

    def _collect_dynamic_settings(self, cfg: dict):
        if cfg["frequency"] == "hourly" and hasattr(self, 'int_ent'):
            val = self.int_ent.get()
            cfg["interval"] = int(val if val.isdigit() else 1)
        elif hasattr(self, 'tm_ent'):
            cfg["time"] = self.tm_ent.get()
            if cfg["frequency"] == "weekly" and hasattr(self, 'day_cb'):
                cfg["day"] = self.day_cb.get()
