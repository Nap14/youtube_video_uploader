import os
import customtkinter as ctk
from tkinter import filedialog
from typing import Dict, Any

from src.core.context import AppContext
from src.gui.base_frame import BaseFrame

class SettingsFrame(BaseFrame):
    def __init__(self, master, ctx: AppContext, **kwargs):
        super().__init__(master, ctx, **kwargs)

    def _create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self, text="Application Settings", font=ctk.CTkFont(size=24, weight="bold")).grid(
            row=0, column=0, padx=30, pady=(30, 20), sticky="w"
        )
        
        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.content.grid_columnconfigure(0, weight=1)
        
        self.entries: Dict[str, ctk.CTkEntry] = {}
        self._init_settings_fields()
        self._init_theme_selector()
        
        ctk.CTkButton(self, text="Save All Settings", command=self._save, width=200, height=40).grid(
            row=2, column=0, pady=20
        )

    def _init_settings_fields(self):
        self._add_field("SCHOOL_ID", "LMS School ID:")
        self._add_field("LMS_TOKEN", "LMS API Token:", is_password=True)
        self._add_path_field("ZOOM_DIR", "Zoom Videos Directory:")

    def _add_field(self, key: str, label: str, is_password: bool = False):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=8)
        
        ctk.CTkLabel(f, text=label, width=150, anchor="w").pack(side="left")
        
        ent = ctk.CTkEntry(f, width=400, show="*" if is_password else "")
        ent.pack(side="left", padx=10)
        ent.insert(0, self.ctx.config.get_data().get(key, ""))
        self.entries[key] = ent
        
        if is_password:
            self._add_toggle_btn(f, ent)

    def _add_toggle_btn(self, parent, entry):
        btn = ctk.CTkButton(
            parent, text="👁", width=30, fg_color="transparent", hover_color=("gray70", "gray30"),
            command=lambda: entry.configure(show="" if entry.cget("show") == "*" else "*")
        )
        btn.pack(side="left")

    def _add_path_field(self, key: str, label: str):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=8)
        
        ctk.CTkLabel(f, text=label, width=150, anchor="w").pack(side="left")
        
        ent = ctk.CTkEntry(f, width=350)
        ent.pack(side="left", padx=10)
        ent.insert(0, self.ctx.config.get_data().get(key, ""))
        self.entries[key] = ent
        
        ctk.CTkButton(
            f, text="Browse", width=40, command=lambda k=key, e=ent: self._browse(k, e)
        ).pack(side="left")

    def _init_theme_selector(self):
        f = ctk.CTkFrame(self.content, fg_color="transparent")
        f.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(f, text="Interface Theme:", width=150, anchor="w").pack(side="left")
        
        self.theme_menu = ctk.CTkOptionMenu(
            f, values=["System", "Light", "Dark"], 
            command=self._change_theme
        )
        self.theme_menu.pack(side="left", padx=10)
        self.theme_menu.set(self.ctx.config.get_data().get("THEME", "Dark"))

    def _browse(self, key, ent):
        d = filedialog.askdirectory()
        if d:
            ent.delete(0, "end")
            ent.insert(0, os.path.normpath(d))

    def _change_theme(self, new_theme: str):
        ctk.set_appearance_mode(new_theme)

    def _save(self):
        data = self.ctx.config.get_data()
        for key, ent in self.entries.items():
            data[key] = ent.get().strip()
        data["THEME"] = self.theme_menu.get()
        
        self.ctx.config.save()
        self._show_feedback()

    def _show_feedback(self):
        btn = self.grid_slaves(row=2, column=0)[0]
        orig_text = btn.cget("text")
        btn.configure(text="Saved Success!", fg_color="#27ae60")
        self.after(2000, lambda: btn.configure(text=orig_text, fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"]))

    def is_dirty(self) -> bool:
        data = self.ctx.config.get_data()
        if data.get("THEME") != self.theme_menu.get():
            return True
        for key, ent in self.entries.items():
            if data.get(key) != ent.get().strip():
                return True
        return False
